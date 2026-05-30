import aiosqlite
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, List

ISO_FMT = "%Y-%m-%dT%H:%M:%S"


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init(self) -> None:
        db_file = Path(self.db_path)
        if db_file.parent != Path("."):
            db_file.parent.mkdir(parents=True, exist_ok=True)

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tg_id INTEGER UNIQUE,
                    full_name TEXT,
                    phone TEXT,
                    region TEXT,
                    purpose TEXT,
                    role TEXT,
                    profession TEXT,
                    bio TEXT,
                    photo_id TEXT,
                    ref_code TEXT,
                    referred_by INTEGER,
                    diamonds INTEGER DEFAULT 0,
                    diamonds_spent INTEGER DEFAULT 0,
                    top_until TEXT,
                    vip_until TEXT,
                    is_blocked INTEGER DEFAULT 0,
                    last_seen TEXT,
                    created_at TEXT
                )
                """
            )
            await self._ensure_column(db, "users", "is_blocked", "INTEGER DEFAULT 0")
            await self._ensure_column(db, "users", "last_seen", "TEXT")
            await self._ensure_column(db, "users", "profession", "TEXT")
            await self._ensure_column(db, "users", "bio", "TEXT")
            await self._ensure_column(db, "users", "photo_id", "TEXT")
            await self._ensure_column(db, "users", "ref_code", "TEXT")
            await self._ensure_column(db, "users", "referred_by", "INTEGER")
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    master_tg_id INTEGER,
                    from_tg_id INTEGER,
                    rating INTEGER,
                    comment TEXT,
                    created_at TEXT
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    from_tg_id INTEGER,
                    to_tg_id INTEGER,
                    order_type TEXT,
                    created_at TEXT
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tg_id INTEGER,
                    amount INTEGER,
                    reason TEXT,
                    created_at TEXT
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_a INTEGER,
                    user_b INTEGER,
                    is_active INTEGER DEFAULT 1,
                    created_at TEXT
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
                """
            )
            await db.commit()

    async def _ensure_column(self, db: aiosqlite.Connection, table: str, column: str, ddl: str) -> None:
        db.row_factory = aiosqlite.Row
        async with db.execute(f"PRAGMA table_info({table})") as cur:
            cols = [row["name"] for row in await cur.fetchall()]
        if column not in cols:
            await db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")

    async def add_user(
        self,
        tg_id: int,
        full_name: str,
        phone: str,
        region: str,
        purpose: str,
        role: str,
        profession: str | None = None,
        bio: str | None = None,
        photo_id: str | None = None,
        ref_code: str | None = None,
        referred_by: int | None = None,
        diamonds: int = 10,
    ) -> None:
        created_at = datetime.utcnow().strftime(ISO_FMT)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO users
                (tg_id, full_name, phone, region, purpose, role, profession, bio, photo_id, ref_code, referred_by, diamonds, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tg_id,
                    full_name,
                    phone,
                    region,
                    purpose,
                    role,
                    profession,
                    bio,
                    photo_id,
                    ref_code,
                    referred_by,
                    diamonds,
                    created_at,
                ),
            )
            await db.commit()

    async def get_user(self, tg_id: int) -> dict[str, Any] | None:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users WHERE tg_id = ?", (tg_id,)) as cur:
                row = await cur.fetchone()
                return dict(row) if row else None

    async def update_user_field(self, tg_id: int, field: str, value: Any) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"UPDATE users SET {field} = ? WHERE tg_id = ?", (value, tg_id))
            await db.commit()

    async def update_last_seen(self, tg_id: int) -> None:
        now = datetime.utcnow().strftime(ISO_FMT)
        await self.update_user_field(tg_id, "last_seen", now)

    async def add_diamonds(self, tg_id: int, amount: int) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET diamonds = diamonds + ? WHERE tg_id = ?",
                (amount, tg_id),
            )
            await db.execute(
                "INSERT INTO transactions (tg_id, amount, reason, created_at) VALUES (?, ?, ?, ?)",
                (tg_id, amount, "add", datetime.utcnow().strftime(ISO_FMT)),
            )
            await db.commit()

    async def deduct_diamonds(self, tg_id: int, amount: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT diamonds FROM users WHERE tg_id = ?", (tg_id,)) as cur:
                row = await cur.fetchone()
                if not row:
                    return False
                if row["diamonds"] < amount:
                    return False
            await db.execute(
                "UPDATE users SET diamonds = diamonds - ?, diamonds_spent = diamonds_spent + ? WHERE tg_id = ?",
                (amount, amount, tg_id),
            )
            await db.execute(
                "INSERT INTO transactions (tg_id, amount, reason, created_at) VALUES (?, ?, ?, ?)",
                (tg_id, -amount, "deduct", datetime.utcnow().strftime(ISO_FMT)),
            )
            await db.commit()
            return True

    async def list_masters(self, limit: int = 10, offset: int = 0) -> list[dict[str, Any]]:
        now = datetime.utcnow().strftime(ISO_FMT)
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = (
                "SELECT *, "
                "(CASE WHEN top_until IS NOT NULL AND top_until > ? THEN 1 ELSE 0 END) AS is_top, "
                "(CASE WHEN vip_until IS NOT NULL AND vip_until > ? THEN 1 ELSE 0 END) AS is_vip "
                "FROM users "
                "WHERE role = 'usta' AND is_blocked = 0 "
                "ORDER BY is_top DESC, is_vip DESC, id DESC "
                "LIMIT ? OFFSET ?"
            )
            async with db.execute(query, (now, now, limit, offset)) as cur:
                rows = await cur.fetchall()
                return [dict(r) for r in rows]

    async def list_masters_by_region(self, region: str) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users WHERE role = 'usta' AND is_blocked = 0 AND lower(region) = lower(?)",
                (region,),
            ) as cur:
                rows = await cur.fetchall()
                return [dict(r) for r in rows]

    async def set_blocked(self, tg_id: int, blocked: bool) -> None:
        await self.update_user_field(tg_id, "is_blocked", 1 if blocked else 0)

    async def list_user_ids(self, include_blocked: bool = False) -> list[int]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if include_blocked:
                query = "SELECT tg_id FROM users"
                params: tuple[Any, ...] = ()
            else:
                query = "SELECT tg_id FROM users WHERE is_blocked = 0"
                params = ()
            async with db.execute(query, params) as cur:
                rows = await cur.fetchall()
                return [int(r["tg_id"]) for r in rows]

    async def list_users(self, limit: int = 200, offset: int = 0) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM users ORDER BY id DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ) as cur:
                rows = await cur.fetchall()
                return [dict(r) for r in rows]

    async def add_diamonds_all(self, amount: int, include_blocked: bool = False) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            if include_blocked:
                query = "UPDATE users SET diamonds = diamonds + ?"
                params: tuple[Any, ...] = (amount,)
            else:
                query = "UPDATE users SET diamonds = diamonds + ? WHERE is_blocked = 0"
                params = (amount,)
            cur = await db.execute(query, params)
            await db.commit()
            return cur.rowcount if cur.rowcount is not None else 0

    async def set_top(self, tg_id: int, days: int = 3) -> None:
        until = (datetime.utcnow() + timedelta(days=days)).strftime(ISO_FMT)
        await self.update_user_field(tg_id, "top_until", until)

    async def set_vip(self, tg_id: int, days: int | None = None) -> None:
        if days is None:
            until = (datetime.utcnow() + timedelta(days=3650)).strftime(ISO_FMT)
        else:
            until = (datetime.utcnow() + timedelta(days=days)).strftime(ISO_FMT)
        await self.update_user_field(tg_id, "vip_until", until)

    async def stats(self) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT COUNT(*) as total_users FROM users") as cur:
                total_users = int((await cur.fetchone())["total_users"])

            async with db.execute("SELECT COALESCE(SUM(diamonds), 0) as total_balance FROM users") as cur:
                total_balance = int((await cur.fetchone())["total_balance"])

            async with db.execute(
                "SELECT COALESCE(SUM(amount), 0) as total_spent FROM transactions WHERE amount < 0"
            ) as cur:
                total_spent = abs(int((await cur.fetchone())["total_spent"]))

            return {"total_users": total_users, "total_balance": total_balance, "total_spent": total_spent}
    
    async def get_all_users(self, limit: int = 50, offset: int = 0) -> List[dict]:
        """Get all users with pagination"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT tg_id, full_name, phone, region, diamonds, is_blocked, created_at, last_seen "
                "FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset)
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_total_users_count(self) -> int:
        """Get total count of users"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT COUNT(*) as count FROM users") as cur:
                result = await cur.fetchone()
                return int(result["count"]) if result else 0

    async def search_users(self, search_term: str) -> list[dict[str, Any]]:
        term = search_term.strip()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if term.isdigit():
                query = "SELECT * FROM users WHERE tg_id = ? ORDER BY id DESC"
                params = (int(term),)
            else:
                like = f"%{term.lower()}%"
                query = (
                    "SELECT * FROM users WHERE "
                    "lower(COALESCE(full_name, '')) LIKE ? OR "
                    "lower(COALESCE(phone, '')) LIKE ? OR "
                    "lower(COALESCE(region, '')) LIKE ? OR "
                    "lower(COALESCE(role, '')) LIKE ? OR "
                    "lower(COALESCE(profession, '')) LIKE ? "
                    "ORDER BY id DESC"
                )
                params = (like, like, like, like, like)
            async with db.execute(query, params) as cur:
                rows = await cur.fetchall()
                return [dict(row) for row in rows]

    async def list_masters_by_profession(self, profession: str, limit: int = 10, offset: int = 0) -> list[dict[str, Any]]:
        now = datetime.utcnow().strftime(ISO_FMT)
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            query = (
                "SELECT *, "
                "(CASE WHEN top_until IS NOT NULL AND top_until > ? THEN 1 ELSE 0 END) AS is_top, "
                "(CASE WHEN vip_until IS NOT NULL AND vip_until > ? THEN 1 ELSE 0 END) AS is_vip "
                "FROM users "
                "WHERE role = 'usta' AND is_blocked = 0 AND lower(profession) = lower(?) "
                "ORDER BY is_top DESC, is_vip DESC, id DESC "
                "LIMIT ? OFFSET ?"
            )
            async with db.execute(query, (now, now, profession, limit, offset)) as cur:
                rows = await cur.fetchall()
                return [dict(r) for r in rows]

    async def get_active_users_count(self) -> int:
        cutoff = (datetime.utcnow() - timedelta(days=7)).strftime(ISO_FMT)
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT COUNT(*) AS count FROM users WHERE last_seen IS NOT NULL AND last_seen >= ?",
                (cutoff,),
            ) as cur:
                row = await cur.fetchone()
                return int(row["count"]) if row else 0

    async def get_blocked_users_count(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT COUNT(*) AS count FROM users WHERE is_blocked = 1") as cur:
                row = await cur.fetchone()
                return int(row["count"]) if row else 0

    async def get_users_with_diamonds_count(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT COUNT(*) AS count FROM users WHERE diamonds > 0") as cur:
                row = await cur.fetchone()
                return int(row["count"]) if row else 0

    async def get_masters_count(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT COUNT(*) AS count FROM users WHERE role = 'usta'") as cur:
                row = await cur.fetchone()
                return int(row["count"]) if row else 0

    async def get_clients_count(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT COUNT(*) AS count FROM users WHERE COALESCE(role, '') != 'usta'") as cur:
                row = await cur.fetchone()
                return int(row["count"]) if row else 0

    async def get_today_users_count(self) -> int:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT COUNT(*) AS count FROM users WHERE substr(created_at, 1, 10) = ?",
                (today,),
            ) as cur:
                row = await cur.fetchone()
                return int(row["count"]) if row else 0

    async def get_user_stats(self, user_id: int) -> dict[str, int]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT COUNT(*) AS searches FROM orders WHERE from_tg_id = ?",
                (user_id,),
            ) as cur:
                searches = int((await cur.fetchone())["searches"])
            async with db.execute(
                "SELECT COUNT(*) AS chats FROM chat_sessions WHERE user_a = ? OR user_b = ?",
                (user_id, user_id),
            ) as cur:
                chats = int((await cur.fetchone())["chats"])
            async with db.execute(
                "SELECT COUNT(*) AS reviews FROM ratings WHERE master_tg_id = ? OR from_tg_id = ?",
                (user_id, user_id),
            ) as cur:
                reviews = int((await cur.fetchone())["reviews"])
            async with db.execute(
                "SELECT COALESCE(ABS(SUM(amount)), 0) AS spent FROM transactions WHERE tg_id = ? AND amount < 0",
                (user_id,),
            ) as cur:
                spent = int((await cur.fetchone())["spent"])
            return {"searches": searches, "chats": chats, "reviews": reviews, "spent": spent}

    async def get_daily_stats(self, day: Any) -> dict[str, int]:
        day_str = str(day)[:10]
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT COUNT(*) AS new_users FROM users WHERE substr(created_at, 1, 10) = ?",
                (day_str,),
            ) as cur:
                new_users = int((await cur.fetchone())["new_users"])
            async with db.execute(
                "SELECT COUNT(*) AS searches FROM orders WHERE substr(created_at, 1, 10) = ?",
                (day_str,),
            ) as cur:
                searches = int((await cur.fetchone())["searches"])
            async with db.execute(
                "SELECT COUNT(*) AS active_chats FROM chat_sessions WHERE is_active = 1",
            ) as cur:
                active_chats = int((await cur.fetchone())["active_chats"])
            async with db.execute(
                "SELECT COALESCE(ABS(SUM(amount)), 0) AS diamonds_spent FROM transactions WHERE amount < 0 AND substr(created_at, 1, 10) = ?",
                (day_str,),
            ) as cur:
                diamonds_spent = int((await cur.fetchone())["diamonds_spent"])
            async with db.execute(
                "SELECT COUNT(*) AS reviews FROM ratings WHERE substr(created_at, 1, 10) = ?",
                (day_str,),
            ) as cur:
                reviews = int((await cur.fetchone())["reviews"])
            async with db.execute(
                "SELECT COUNT(*) AS blocked_users FROM users WHERE is_blocked = 1",
            ) as cur:
                blocked_users = int((await cur.fetchone())["blocked_users"])

            return {
                "new_users": new_users,
                "searches": searches,
                "active_chats": active_chats,
                "diamonds_spent": diamonds_spent,
                "revenue": diamonds_spent,
                "reviews": reviews,
                "blocked_users": blocked_users,
                "morning_activity": 0,
                "afternoon_activity": 0,
                "evening_activity": 0,
                "night_activity": 0,
            }

    async def get_diamond_stats(self) -> dict[str, int | float]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT diamonds FROM users ORDER BY diamonds DESC") as cur:
                balances = [int(row["diamonds"] or 0) for row in await cur.fetchall()]
            total_users = len(balances)
            total_diamonds = sum(balances)
            users_with_diamonds = sum(1 for value in balances if value > 0)

            async with db.execute(
                "SELECT COALESCE(ABS(SUM(amount)), 0) AS spent_today FROM transactions WHERE amount < 0 AND substr(created_at, 1, 10) = ?",
                (datetime.utcnow().strftime("%Y-%m-%d"),),
            ) as cur:
                spent_today = int((await cur.fetchone())["spent_today"])

            async with db.execute(
                "SELECT COALESCE(ABS(SUM(amount)), 0) AS spent_week FROM transactions WHERE amount < 0 AND created_at >= ?",
                ((datetime.utcnow() - timedelta(days=7)).strftime(ISO_FMT),),
            ) as cur:
                spent_week = int((await cur.fetchone())["spent_week"])

            async with db.execute(
                "SELECT COALESCE(ABS(SUM(amount)), 0) AS spent_month FROM transactions WHERE amount < 0 AND created_at >= ?",
                ((datetime.utcnow() - timedelta(days=30)).strftime(ISO_FMT),),
            ) as cur:
                spent_month = int((await cur.fetchone())["spent_month"])

            async with db.execute(
                "SELECT COALESCE(SUM(amount), 0) AS bonus_given FROM transactions WHERE amount > 0",
            ) as cur:
                bonus_given = int((await cur.fetchone())["bonus_given"])

            avg_balance = (total_diamonds / total_users) if total_users else 0
            top_10_percent = int(total_users * 0.1)
            top_25_percent = int(total_users * 0.25)
            top_50_percent = int(total_users * 0.5)

            return {
                "total_diamonds": total_diamonds,
                "users_with_diamonds": users_with_diamonds,
                "spent_today": spent_today,
                "spent_week": spent_week,
                "spent_month": spent_month,
                "bonus_given": bonus_given,
                "avg_balance": avg_balance,
                "top_10_percent": top_10_percent,
                "top_25_percent": top_25_percent,
                "top_50_percent": top_50_percent,
            }

    async def add_rating(self, master_tg_id: int, from_tg_id: int, rating: int, comment: str | None) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO ratings (master_tg_id, from_tg_id, rating, comment, created_at) VALUES (?, ?, ?, ?, ?)",
                (master_tg_id, from_tg_id, rating, comment, datetime.utcnow().strftime(ISO_FMT)),
            )
            await db.commit()

    async def get_master_rating(self, master_tg_id: int) -> tuple[float, int]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT COALESCE(AVG(rating),0), COUNT(*) FROM ratings WHERE master_tg_id = ?",
                (master_tg_id,),
            ) as cur:
                row = await cur.fetchone()
                return float(row[0]), int(row[1])

    async def add_order(self, from_tg_id: int, to_tg_id: int, order_type: str) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO orders (from_tg_id, to_tg_id, order_type, created_at) VALUES (?, ?, ?, ?)",
                (from_tg_id, to_tg_id, order_type, datetime.utcnow().strftime(ISO_FMT)),
            )
            await db.commit()

    async def list_orders_for_user(self, tg_id: int, limit: int = 20) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM orders WHERE from_tg_id = ? ORDER BY id DESC LIMIT ?",
                (tg_id, limit),
            ) as cur:
                rows = await cur.fetchall()
                return [dict(r) for r in rows]

    async def list_orders_for_master(self, tg_id: int, limit: int = 20) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM orders WHERE to_tg_id = ? ORDER BY id DESC LIMIT ?",
                (tg_id, limit),
            ) as cur:
                rows = await cur.fetchall()
                return [dict(r) for r in rows]

    async def list_transactions(self, tg_id: int, limit: int = 20) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM transactions WHERE tg_id = ? ORDER BY id DESC LIMIT ?",
                (tg_id, limit),
            ) as cur:
                rows = await cur.fetchall()
                return [dict(r) for r in rows]

    async def get_by_ref_code(self, ref_code: str) -> dict[str, Any] | None:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users WHERE ref_code = ?", (ref_code,)) as cur:
                row = await cur.fetchone()
                return dict(row) if row else None

    async def delete_user(self, tg_id: int) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM users WHERE tg_id = ?", (tg_id,))
            await db.execute("DELETE FROM ratings WHERE master_tg_id = ? OR from_tg_id = ?", (tg_id, tg_id))
            await db.execute("DELETE FROM orders WHERE from_tg_id = ? OR to_tg_id = ?", (tg_id, tg_id))
            await db.execute("DELETE FROM transactions WHERE tg_id = ?", (tg_id,))
            await db.execute("DELETE FROM chat_sessions WHERE user_a = ? OR user_b = ?", (tg_id, tg_id))
            await db.commit()

    async def get_setting(self, key: str, default: str | None = None) -> str | None:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT value FROM settings WHERE key = ?", (key,)) as cur:
                row = await cur.fetchone()
                return row[0] if row else default

    async def set_setting(self, key: str, value: str) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )
            await db.commit()

    async def is_paid_mode(self) -> bool:
        value = await self.get_setting("paid_mode", "true")
        return str(value).lower() in {"1", "true", "yes", "on"}

    async def start_chat(self, user_a: int, user_b: int) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            # close existing chats for these users
            await db.execute(
                "UPDATE chat_sessions SET is_active = 0 WHERE user_a IN (?, ?) OR user_b IN (?, ?)",
                (user_a, user_b, user_a, user_b),
            )
            await db.execute(
                "INSERT INTO chat_sessions (user_a, user_b, is_active, created_at) VALUES (?, ?, 1, ?)",
                (user_a, user_b, datetime.utcnow().strftime(ISO_FMT)),
            )
            await db.commit()

    async def get_chat_partner(self, tg_id: int) -> int | None:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT user_a, user_b FROM chat_sessions WHERE is_active = 1 AND (user_a = ? OR user_b = ?) ORDER BY id DESC LIMIT 1",
                (tg_id, tg_id),
            ) as cur:
                row = await cur.fetchone()
                if not row:
                    return None
                user_a, user_b = row
                return user_b if user_a == tg_id else user_a

    async def end_chat(self, tg_id: int) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cur = await db.execute(
                "UPDATE chat_sessions SET is_active = 0 WHERE is_active = 1 AND (user_a = ? OR user_b = ?)",
                (tg_id, tg_id),
            )
            await db.commit()
            return (cur.rowcount or 0) > 0
