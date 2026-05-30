"""
Firebase Database Integration for Usta Top Bot.

This adapter mirrors the SQLite database interface used by the handlers,
but stores data in Cloud Firestore.
"""

from __future__ import annotations

import asyncio
import json
import math
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import firebase_admin
from firebase_admin import credentials, firestore, initialize_app


def _parse_iso(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except Exception:
        return None


def _normalize_private_key(value: str | None) -> str | None:
    if not value:
        return None
    return value.replace("\\n", "\n")


class FirebaseDB:
    """Firestore-backed database manager."""

    def __init__(self, credentials_path: str | None = None):
        self.app = None
        self.db = None
        self.credentials_path = credentials_path
        self._initialized = False

    @property
    def users(self):
        return self.db.collection("users")

    @property
    def ratings(self):
        return self.db.collection("ratings")

    @property
    def orders(self):
        return self.db.collection("orders")

    @property
    def transactions(self):
        return self.db.collection("transactions")

    @property
    def chats(self):
        return self.db.collection("chat_sessions")

    @property
    def settings(self):
        return self.db.collection("settings")

    async def _run(self, func):
        return await asyncio.to_thread(func)

    def _service_account_from_env(self) -> dict[str, Any] | None:
        project_id = os.getenv("FIREBASE_PROJECT_ID", "").strip() or None
        private_key = _normalize_private_key(os.getenv("FIREBASE_PRIVATE_KEY", "").strip() or None)
        client_email = os.getenv("FIREBASE_CLIENT_EMAIL", "").strip() or None
        if not (project_id and private_key and client_email):
            return None

        config: dict[str, Any] = {
            "type": "service_account",
            "project_id": project_id,
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID", "").strip() or None,
            "private_key": private_key,
            "client_email": client_email,
            "client_id": os.getenv("FIREBASE_CLIENT_ID", "").strip() or None,
            "auth_uri": os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
            "auth_provider_x509_cert_url": os.getenv(
                "FIREBASE_AUTH_PROVIDER_X509_CERT_URL",
                "https://www.googleapis.com/oauth2/v1/certs",
            ),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL", "").strip() or None,
        }
        return {key: value for key, value in config.items() if value is not None}

    def _service_account_from_json(self, raw_json: str) -> dict[str, Any]:
        data = json.loads(raw_json)
        if "private_key" in data:
            data["private_key"] = _normalize_private_key(data["private_key"])
        return data

    def _load_credentials(self):
        explicit_file = self.credentials_path or os.getenv("FIREBASE_CREDENTIALS_FILE", "").strip()
        if explicit_file and os.path.exists(explicit_file):
            return credentials.Certificate(explicit_file)

        env_json = os.getenv("FIREBASE_CREDENTIALS_JSON", "").strip()
        if env_json:
            if os.path.exists(env_json):
                return credentials.Certificate(env_json)
            return credentials.Certificate(self._service_account_from_json(env_json))

        default_file = "firebase_credentials.json"
        if os.path.exists(default_file):
            return credentials.Certificate(default_file)

        env_account = self._service_account_from_env()
        if env_account:
            return credentials.Certificate(env_account)

        return None

    async def _verify_database_ready(self) -> None:
        def _check():
            self.db.collection("_healthcheck").document("_ping").get()

        try:
            await self._run(_check)
        except Exception as exc:
            message = str(exc)
            if "database (default) does not exist" in message.lower():
                raise RuntimeError(
                    "Firestore database is not created for this project. "
                    "Enable Cloud Firestore/Datastore in the Firebase console first."
                ) from exc
            raise

    async def init(self):
        """Initialize Firebase connection."""
        try:
            if firebase_admin._apps:
                self.app = firebase_admin.get_app()
                print("🔥 Using existing Firebase app")
            else:
                cred = self._load_credentials()
                if cred is not None:
                    self.app = initialize_app(cred)
                    print("🔥 Using Firebase service account credentials")
                else:
                    self.app = initialize_app()
                    print("🔥 Using Firebase application default credentials")

            self.db = firestore.client()
            await self._verify_database_ready()
            self._initialized = True
            print("✅ Firebase initialized successfully")
        except Exception as e:
            print(f"❌ Firebase initialization error: {e}")
            raise

    async def _ensure_initialized(self):
        if not self._initialized:
            await self.init()

    def _user_from_snapshot(self, doc) -> dict[str, Any] | None:
        if not doc.exists:
            return None
        data = doc.to_dict() or {}
        data["tg_id"] = int(doc.id)
        return data

    async def _all_users(self) -> list[dict[str, Any]]:
        await self._ensure_initialized()

        def _load():
            return [self._user_from_snapshot(doc) for doc in self.users.stream()]

        users = await self._run(_load)
        return [user for user in users if user]

    def _sort_users(self, users: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(
            users,
            key=lambda user: (
                user.get("created_at") or "",
                int(user.get("tg_id", 0)),
            ),
            reverse=True,
        )

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
        await self._ensure_initialized()
        now = datetime.utcnow().isoformat()
        payload = {
            "tg_id": tg_id,
            "full_name": full_name,
            "phone": phone,
            "region": region,
            "purpose": purpose,
            "role": role,
            "profession": profession,
            "bio": bio,
            "photo_id": photo_id,
            "ref_code": ref_code,
            "referred_by": referred_by,
            "diamonds": diamonds,
            "diamonds_spent": 0,
            "top_until": None,
            "vip_until": None,
            "is_blocked": 0,
            "last_seen": None,
            "created_at": now,
            "updated_at": now,
        }

        def _write():
            self.users.document(str(tg_id)).set(payload)

        await self._run(_write)

    async def get_user(self, tg_id: int) -> dict[str, Any] | None:
        await self._ensure_initialized()

        def _load():
            return self._user_from_snapshot(self.users.document(str(tg_id)).get())

        return await self._run(_load)

    async def update_user(self, tg_id: int, updates: Dict[str, Any]) -> bool:
        await self._ensure_initialized()
        payload = dict(updates)
        payload["updated_at"] = datetime.utcnow().isoformat()

        def _write():
            self.users.document(str(tg_id)).set(payload, merge=True)
            return True

        return await self._run(_write)

    async def update_user_field(self, tg_id: int, field: str, value: Any) -> None:
        await self.update_user(tg_id, {field: value})

    async def update_last_seen(self, tg_id: int) -> None:
        await self.update_user_field(tg_id, "last_seen", datetime.utcnow().isoformat())

    async def add_diamonds(self, tg_id: int, amount: int, reason: str = "") -> bool:
        await self._ensure_initialized()
        user = await self.get_user(tg_id)
        if not user:
            return False

        new_balance = int(user.get("diamonds", 0)) + amount
        new_spent = int(user.get("diamonds_spent", 0))
        if amount < 0:
            new_spent += abs(amount)

        payload = {
            "diamonds": new_balance,
            "diamonds_spent": new_spent,
            "updated_at": datetime.utcnow().isoformat(),
        }

        def _write():
            self.users.document(str(tg_id)).set(payload, merge=True)
            self.transactions.add(
                {
                    "tg_id": tg_id,
                    "amount": amount,
                    "reason": reason or ("add" if amount >= 0 else "deduct"),
                    "created_at": datetime.utcnow().isoformat(),
                }
            )
            return True

        return await self._run(_write)

    async def deduct_diamonds(self, tg_id: int, amount: int) -> bool:
        user = await self.get_user(tg_id)
        if not user:
            return False
        current = int(user.get("diamonds", 0))
        if current < amount:
            return False
        return await self.add_diamonds(tg_id, -amount, reason="deduct")

    async def list_masters(self, limit: int = 10, offset: int = 0) -> list[dict[str, Any]]:
        users = await self._all_users()
        now = datetime.utcnow().isoformat()
        masters = [u for u in users if u.get("role") == "usta" and int(u.get("is_blocked", 0)) == 0]
        for user in masters:
            top_until = user.get("top_until")
            vip_until = user.get("vip_until")
            user["is_top"] = 1 if top_until and str(top_until) > now else 0
            user["is_vip"] = 1 if vip_until and str(vip_until) > now else 0
        masters.sort(key=lambda u: (u.get("is_top", 0), u.get("is_vip", 0), int(u.get("tg_id", 0))), reverse=True)
        return masters[offset : offset + limit]

    async def list_masters_by_region(self, region: str) -> list[dict[str, Any]]:
        users = await self._all_users()
        region_lower = region.strip().lower()
        masters = [
            user
            for user in users
            if user.get("role") == "usta"
            and int(user.get("is_blocked", 0)) == 0
            and str(user.get("region", "")).strip().lower() == region_lower
        ]
        return self._sort_users(masters)

    async def list_masters_by_profession(self, profession: str, limit: int = 10, offset: int = 0) -> list[dict[str, Any]]:
        users = await self._all_users()
        profession_lower = profession.strip().lower()
        masters = [
            user
            for user in users
            if user.get("role") == "usta"
            and int(user.get("is_blocked", 0)) == 0
            and str(user.get("profession", "")).strip().lower() == profession_lower
        ]
        now = datetime.utcnow().isoformat()
        for user in masters:
            top_until = user.get("top_until")
            vip_until = user.get("vip_until")
            user["is_top"] = 1 if top_until and str(top_until) > now else 0
            user["is_vip"] = 1 if vip_until and str(vip_until) > now else 0
        masters.sort(key=lambda u: (u.get("is_top", 0), u.get("is_vip", 0), int(u.get("tg_id", 0))), reverse=True)
        return masters[offset : offset + limit]

    async def set_blocked(self, tg_id: int, blocked: bool) -> None:
        await self.update_user_field(tg_id, "is_blocked", 1 if blocked else 0)

    async def list_user_ids(self, include_blocked: bool = False) -> list[int]:
        users = await self._all_users()
        filtered = users if include_blocked else [u for u in users if int(u.get("is_blocked", 0)) == 0]
        return [int(user["tg_id"]) for user in filtered]

    async def add_diamonds_all(self, amount: int, include_blocked: bool = False) -> int:
        users = await self._all_users()
        target_users = users if include_blocked else [u for u in users if int(u.get("is_blocked", 0)) == 0]
        updated = 0
        for user in target_users:
            ok = await self.add_diamonds(int(user["tg_id"]), amount)
            if ok:
                updated += 1
        return updated

    async def set_top(self, tg_id: int, days: int = 3) -> None:
        until = (datetime.utcnow() + timedelta(days=days)).isoformat()
        await self.update_user_field(tg_id, "top_until", until)

    async def set_vip(self, tg_id: int, days: int | None = None) -> None:
        until = (datetime.utcnow() + timedelta(days=3650 if days is None else days)).isoformat()
        await self.update_user_field(tg_id, "vip_until", until)

    async def get_all_users(self, limit: int = 50, offset: int = 0) -> List[dict]:
        users = self._sort_users(await self._all_users())
        return users[offset : offset + limit]

    async def get_total_users_count(self) -> int:
        return len(await self._all_users())

    async def search_users(self, search_term: str) -> list[dict[str, Any]]:
        users = await self._all_users()
        term = search_term.strip().lower()
        if term.isdigit():
            return [user for user in users if str(user.get("tg_id")) == term]
        return [
            user
            for user in users
            if term in str(user.get("full_name", "")).lower()
            or term in str(user.get("phone", "")).lower()
            or term in str(user.get("region", "")).lower()
            or term in str(user.get("role", "")).lower()
            or term in str(user.get("profession", "")).lower()
        ]

    async def get_active_users_count(self) -> int:
        cutoff = datetime.utcnow() - timedelta(days=7)
        users = await self._all_users()
        count = 0
        for user in users:
            last_seen = _parse_iso(user.get("last_seen"))
            if last_seen and last_seen >= cutoff:
                count += 1
        return count

    async def get_blocked_users_count(self) -> int:
        users = await self._all_users()
        return sum(1 for user in users if int(user.get("is_blocked", 0)) == 1)

    async def get_users_with_diamonds_count(self) -> int:
        users = await self._all_users()
        return sum(1 for user in users if int(user.get("diamonds", 0)) > 0)

    async def get_masters_count(self) -> int:
        users = await self._all_users()
        return sum(1 for user in users if user.get("role") == "usta")

    async def get_clients_count(self) -> int:
        users = await self._all_users()
        return sum(1 for user in users if user.get("role") != "usta")

    async def get_today_users_count(self) -> int:
        today = datetime.utcnow().date()
        users = await self._all_users()
        count = 0
        for user in users:
            created_at = _parse_iso(user.get("created_at"))
            if created_at and created_at.date() == today:
                count += 1
        return count

    async def get_user_stats(self, user_id: int) -> dict[str, int]:
        orders = await self.list_orders_for_user(user_id, limit=1000)
        chats = await self._run(
            lambda: list(self.chats.where("user_a", "==", user_id).stream())
        )
        chat_docs = await self._run(
            lambda: list(self.chats.where("user_b", "==", user_id).stream())
        )
        ratings = await self._run(
            lambda: list(self.ratings.where("master_tg_id", "==", user_id).stream())
        )
        sent_ratings = await self._run(
            lambda: list(self.ratings.where("from_tg_id", "==", user_id).stream())
        )
        transactions = await self.list_transactions(user_id, limit=1000)
        spent = sum(abs(int(row.get("amount", 0))) for row in transactions if int(row.get("amount", 0)) < 0)
        return {
            "searches": len(orders),
            "chats": len(chats) + len(chat_docs),
            "reviews": len(ratings) + len(sent_ratings),
            "spent": spent,
        }

    async def get_daily_stats(self, day: Any) -> dict[str, int]:
        day_str = str(day)[:10]
        users = await self._all_users()
        orders = await self._run(lambda: list(self.orders.stream()))
        chats = await self._run(lambda: list(self.chats.where("is_active", "==", 1).stream()))
        ratings = await self._run(lambda: list(self.ratings.stream()))
        transactions = await self._run(lambda: list(self.transactions.stream()))

        def _created_on(item):
            return str(item.to_dict().get("created_at", ""))[:10]

        new_users = sum(1 for user in users if str(user.get("created_at", ""))[:10] == day_str)
        searches = sum(1 for doc in orders if _created_on(doc) == day_str)
        diamonds_spent = sum(
            abs(int(doc.to_dict().get("amount", 0)))
            for doc in transactions
            if _created_on(doc) == day_str and int(doc.to_dict().get("amount", 0)) < 0
        )
        reviews = sum(1 for doc in ratings if _created_on(doc) == day_str)
        blocked_users = sum(1 for user in users if int(user.get("is_blocked", 0)) == 1)
        active_chats = len(chats)
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
        users = await self._all_users()
        transactions = await self._run(lambda: list(self.transactions.stream()))
        balances = [int(user.get("diamonds", 0)) for user in users]
        total_users = len(users)
        total_diamonds = sum(balances)
        users_with_diamonds = sum(1 for balance in balances if balance > 0)
        today_str = datetime.utcnow().strftime("%Y-%m-%d")

        def _created_on(doc):
            return str(doc.to_dict().get("created_at", ""))[:10]

        spent_today = sum(
            abs(int(doc.to_dict().get("amount", 0)))
            for doc in transactions
            if _created_on(doc) == today_str and int(doc.to_dict().get("amount", 0)) < 0
        )
        spent_week = sum(
            abs(int(doc.to_dict().get("amount", 0)))
            for doc in transactions
            if _parse_iso(doc.to_dict().get("created_at"))
            and _parse_iso(doc.to_dict().get("created_at")) >= datetime.utcnow() - timedelta(days=7)
            and int(doc.to_dict().get("amount", 0)) < 0
        )
        spent_month = sum(
            abs(int(doc.to_dict().get("amount", 0)))
            for doc in transactions
            if _parse_iso(doc.to_dict().get("created_at"))
            and _parse_iso(doc.to_dict().get("created_at")) >= datetime.utcnow() - timedelta(days=30)
            and int(doc.to_dict().get("amount", 0)) < 0
        )
        bonus_given = sum(int(doc.to_dict().get("amount", 0)) for doc in transactions if int(doc.to_dict().get("amount", 0)) > 0)
        avg_balance = (total_diamonds / total_users) if total_users else 0
        return {
            "total_diamonds": total_diamonds,
            "users_with_diamonds": users_with_diamonds,
            "spent_today": spent_today,
            "spent_week": spent_week,
            "spent_month": spent_month,
            "bonus_given": bonus_given,
            "avg_balance": avg_balance,
            "top_10_percent": math.ceil(total_users * 0.1),
            "top_25_percent": math.ceil(total_users * 0.25),
            "top_50_percent": math.ceil(total_users * 0.5),
        }

    async def stats(self) -> dict:
        users = await self._all_users()
        transactions = await self._run(lambda: list(self.transactions.where("amount", "<", 0).stream()))
        total_balance = sum(int(user.get("diamonds", 0)) for user in users)
        total_spent = sum(abs(int(doc.to_dict().get("amount", 0))) for doc in transactions)
        return {
            "total_users": len(users),
            "total_balance": total_balance,
            "total_spent": total_spent,
        }

    async def add_rating(self, master_tg_id: int, from_tg_id: int, rating: int, comment: str | None) -> None:
        await self._ensure_initialized()
        await self._run(
            lambda: self.ratings.add(
                {
                    "master_tg_id": master_tg_id,
                    "from_tg_id": from_tg_id,
                    "rating": rating,
                    "comment": comment,
                    "created_at": datetime.utcnow().isoformat(),
                }
            )
        )

    async def get_master_rating(self, master_tg_id: int) -> tuple[float, int]:
        docs = await self._run(lambda: list(self.ratings.where("master_tg_id", "==", master_tg_id).stream()))
        ratings = [int(doc.to_dict().get("rating", 0)) for doc in docs]
        if not ratings:
            return 0.0, 0
        return sum(ratings) / len(ratings), len(ratings)

    async def add_order(self, from_tg_id: int, to_tg_id: int, order_type: str) -> None:
        await self._ensure_initialized()
        await self._run(
            lambda: self.orders.add(
                {
                    "from_tg_id": from_tg_id,
                    "to_tg_id": to_tg_id,
                    "order_type": order_type,
                    "created_at": datetime.utcnow().isoformat(),
                }
            )
        )

    async def list_orders_for_user(self, tg_id: int, limit: int = 20) -> list[dict[str, Any]]:
        docs = await self._run(lambda: list(self.orders.where("from_tg_id", "==", tg_id).stream()))
        orders = [dict(doc.to_dict(), id=doc.id) for doc in docs]
        orders.sort(key=lambda row: row.get("created_at", ""), reverse=True)
        return orders[:limit]

    async def list_orders_for_master(self, tg_id: int, limit: int = 20) -> list[dict[str, Any]]:
        docs = await self._run(lambda: list(self.orders.where("to_tg_id", "==", tg_id).stream()))
        orders = [dict(doc.to_dict(), id=doc.id) for doc in docs]
        orders.sort(key=lambda row: row.get("created_at", ""), reverse=True)
        return orders[:limit]

    async def list_transactions(self, tg_id: int, limit: int = 20) -> list[dict[str, Any]]:
        docs = await self._run(lambda: list(self.transactions.where("tg_id", "==", tg_id).stream()))
        rows = [dict(doc.to_dict(), id=doc.id) for doc in docs]
        rows.sort(key=lambda row: row.get("created_at", ""), reverse=True)
        return rows[:limit]

    async def get_by_ref_code(self, ref_code: str) -> dict[str, Any] | None:
        users = await self._all_users()
        for user in users:
            if user.get("ref_code") == ref_code:
                return user
        return None

    async def delete_user(self, tg_id: int) -> None:
        await self._ensure_initialized()

        def _delete():
            self.users.document(str(tg_id)).delete()
            for collection in (self.ratings, self.orders, self.transactions, self.chats):
                for doc in collection.where("master_tg_id", "==", tg_id).stream():
                    doc.reference.delete()
                for doc in collection.where("from_tg_id", "==", tg_id).stream():
                    doc.reference.delete()
                for doc in collection.where("to_tg_id", "==", tg_id).stream():
                    doc.reference.delete()
                for doc in collection.where("tg_id", "==", tg_id).stream():
                    doc.reference.delete()
                for doc in collection.where("user_a", "==", tg_id).stream():
                    doc.reference.delete()
                for doc in collection.where("user_b", "==", tg_id).stream():
                    doc.reference.delete()

        await self._run(_delete)

    async def get_setting(self, key: str, default: str | None = None) -> str | None:
        await self._ensure_initialized()

        def _load():
            doc = self.settings.document(key).get()
            return doc.to_dict().get("value") if doc.exists else default

        return await self._run(_load)

    async def set_setting(self, key: str, value: str) -> None:
        await self._ensure_initialized()
        await self._run(lambda: self.settings.document(key).set({"value": value, "updated_at": datetime.utcnow().isoformat()}))

    async def is_paid_mode(self) -> bool:
        value = await self.get_setting("paid_mode", "true")
        return str(value).lower() in {"1", "true", "yes", "on"}

    async def start_chat(self, user_a: int, user_b: int) -> None:
        await self._ensure_initialized()

        def _write():
            for doc in self.chats.stream():
                data = doc.to_dict() or {}
                if data.get("is_active") == 1 and (data.get("user_a") in {user_a, user_b} or data.get("user_b") in {user_a, user_b}):
                    doc.reference.update({"is_active": 0, "updated_at": datetime.utcnow().isoformat()})
            self.chats.add(
                {
                    "user_a": user_a,
                    "user_b": user_b,
                    "is_active": 1,
                    "created_at": datetime.utcnow().isoformat(),
                }
            )

        await self._run(_write)

    async def get_chat_partner(self, tg_id: int) -> int | None:
        docs = await self._run(lambda: list(self.chats.where("is_active", "==", 1).stream()))
        sessions = [doc.to_dict() for doc in docs]
        sessions.sort(key=lambda row: row.get("created_at", ""), reverse=True)
        for session in sessions:
            if session.get("user_a") == tg_id:
                return int(session.get("user_b"))
            if session.get("user_b") == tg_id:
                return int(session.get("user_a"))
        return None

    async def end_chat(self, tg_id: int) -> bool:
        await self._ensure_initialized()
        ended = False

        def _write():
            nonlocal ended
            for doc in self.chats.where("is_active", "==", 1).stream():
                data = doc.to_dict() or {}
                if data.get("user_a") == tg_id or data.get("user_b") == tg_id:
                    doc.reference.update({"is_active": 0, "updated_at": datetime.utcnow().isoformat()})
                    ended = True

        await self._run(_write)
        return ended

    async def create_user(self, user_data: Dict[str, Any]) -> str:
        await self._ensure_initialized()
        user = dict(user_data)
        user["created_at"] = datetime.utcnow().isoformat()
        user["updated_at"] = datetime.utcnow().isoformat()
        tg_id = str(user["tg_id"])
        await self._run(lambda: self.users.document(tg_id).set(user))
        return tg_id

    async def get_all_users_count(self) -> int:
        return await self.get_total_users_count()

    async def create_review(self, review_data: Dict[str, Any]) -> str:
        await self._ensure_initialized()
        payload = dict(review_data)
        payload["created_at"] = datetime.utcnow().isoformat()
        ref = await self._run(lambda: self.ratings.add(payload))
        return ref[1].id

    async def get_user_reviews(self, tg_id: int) -> List[Dict[str, Any]]:
        docs = await self._run(lambda: list(self.ratings.where("master_tg_id", "==", tg_id).stream()))
        reviews = [dict(doc.to_dict(), id=doc.id) for doc in docs]
        reviews.sort(key=lambda row: row.get("created_at", ""), reverse=True)
        return reviews

    async def create_chat(self, chat_data: Dict[str, Any]) -> str:
        await self._ensure_initialized()
        payload = dict(chat_data)
        payload["created_at"] = datetime.utcnow().isoformat()
        ref = await self._run(lambda: self.chats.add(payload))
        return ref[1].id

    async def add_chat_message(self, chat_id: str, message_data: Dict[str, Any]) -> str:
        await self._ensure_initialized()
        payload = dict(message_data)
        payload["created_at"] = datetime.utcnow().isoformat()
        ref = await self._run(lambda: self.db.collection("chats").document(chat_id).collection("messages").add(payload))
        return ref[1].id

    async def get_chat_messages(self, chat_id: str) -> List[Dict[str, Any]]:
        docs = await self._run(
            lambda: list(self.db.collection("chats").document(chat_id).collection("messages").stream())
        )
        messages = [dict(doc.to_dict(), id=doc.id) for doc in docs]
        messages.sort(key=lambda row: row.get("created_at", ""))
        return messages

    async def migrate_from_sqlite(self, sqlite_db_path: str):
        await self._ensure_initialized()
        from db import Database as SQLiteDatabase

        sqlite_db = SQLiteDatabase(sqlite_db_path)
        await sqlite_db.init()
        print("🔄 Starting migration from SQLite to Firebase...")
        sqlite_users = await sqlite_db.get_all_users(limit=1000)
        migrated_count = 0
        for user in sqlite_users:
            firebase_user = {
                "tg_id": user.get("tg_id"),
                "full_name": user.get("full_name"),
                "phone": user.get("phone"),
                "email": user.get("email"),
                "region": user.get("region"),
                "purpose": user.get("purpose"),
                "role": user.get("role"),
                "diamonds": user.get("diamonds", 0),
                "diamonds_spent": user.get("diamonds_spent", 0),
                "top_until": user.get("top_until"),
                "vip_until": user.get("vip_until"),
                "is_blocked": user.get("is_blocked", 0),
                "last_seen": user.get("last_seen"),
                "profession": user.get("profession"),
                "bio": user.get("bio"),
                "photo_id": user.get("photo_id"),
                "ref_code": user.get("ref_code"),
                "referred_by": user.get("referred_by"),
            }
            await self.create_user(firebase_user)
            migrated_count += 1
            if migrated_count % 10 == 0:
                print(f"📊 Migrated {migrated_count} users...")
        print(f"✅ Migration completed! Migrated {migrated_count} users to Firebase")

    def get_firebase_config(self):
        """Compatibility helper kept for existing docs/tests."""
        firebase_config = {
            "type": os.getenv("FIREBASE_TYPE"),
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": _normalize_private_key(os.getenv("FIREBASE_PRIVATE_KEY")),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
            "auth_provider_x509_cert_url": os.getenv(
                "FIREBASE_AUTH_PROVIDER_X509_CERT_URL",
                "https://www.googleapis.com/oauth2/v1/certs",
            ),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
        }
        return {key: value for key, value in firebase_config.items() if value is not None}


firebase_db = FirebaseDB()
