"""
Database Factory - Handles both SQLite and Firebase databases
"""

from config import load_config
from db import Database as SQLiteDatabase
from firebase_db import FirebaseDB

def get_database():
    """Get database instance based on configuration"""
    config = load_config()
    
    if config.db_type == "firebase":
        print("🔥 Using Firebase database")
        return FirebaseDB()
    else:
        print("📁 Using SQLite database")
        return SQLiteDatabase(config.db_path)

# Export the database factory function
__all__ = ['get_database']
