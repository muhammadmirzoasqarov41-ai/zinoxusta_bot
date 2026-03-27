import aiosqlite
from datetime import datetime, timedelta
from typing import Any

ISO_FMT = "%Y-%m-%dT%H:%M:%S"


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path

    async def init(self) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tg_id INTEGER UNIQUE,
                    full_name TEXT,
                    phone TEXT,
                    email TEXT,
                    region TEXT,
                    purpose TEXT,
                    role TEXT,
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
        email: str,
        region: str,
        purpose: str,
        role: str,
        diamonds: int = 10,
    ) -> None:
        created_at = datetime.utcnow().strftime(ISO_FMT)
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO users
                (tg_id, full_name, phone, email, region, purpose, role, diamonds, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (tg_id, full_name, phone, email, region, purpose, role, diamonds, created_at),
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

    async def stats(self) -> dict[str, int]:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cur:
                total_users = (await cur.fetchone())[0]
            async with db.execute("SELECT COALESCE(SUM(diamonds_spent), 0) FROM users") as cur:
                total_spent = (await cur.fetchone())[0]
            async with db.execute("SELECT COALESCE(SUM(diamonds), 0) FROM users") as cur:
                total_balance = (await cur.fetchone())[0]
        return {
            "total_users": int(total_users),
            "total_spent": int(total_spent),
            "total_balance": int(total_balance),
        }
