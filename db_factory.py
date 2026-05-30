"""
Database Factory - Handles both SQLite and Firebase databases
"""

from config import load_config
from db import Database as SQLiteDatabase
from firebase_db import FirebaseDB

_DATABASE_CACHE = None
_DATABASE_CACHE_KEY = None

def get_database():
    """Get database instance based on configuration"""
    global _DATABASE_CACHE, _DATABASE_CACHE_KEY
    config = load_config()
    cache_key = (config.db_type, config.db_path)
    if _DATABASE_CACHE is not None and _DATABASE_CACHE_KEY == cache_key:
        return _DATABASE_CACHE

    if config.db_type == "firebase":
        print("🔥 Using Firebase database")
        _DATABASE_CACHE = FirebaseDB()
    else:
        print("📁 Using SQLite database")
        _DATABASE_CACHE = SQLiteDatabase(config.db_path)
    _DATABASE_CACHE_KEY = cache_key
    return _DATABASE_CACHE

# Export the database factory function
__all__ = ['get_database']
