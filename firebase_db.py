"""
Firebase Database Integration for Usta Top Bot
This module provides Firebase Firestore integration as an alternative to SQLite
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from firebase_admin import credentials, firestore, initialize_app
from google.cloud.firestore_v1.base_query import BaseQuery
import asyncio

class FirebaseDB:
    """Firebase Firestore Database Manager"""
    
    def __init__(self, credentials_path: str = None):
        self.app = None
        self.db = None
        self.credentials_path = credentials_path
        self._initialized = False
    
    async def init(self):
        """Initialize Firebase connection"""
        try:
            if self.credentials_path and os.path.exists(self.credentials_path):
                # Use service account file
                cred = credentials.Certificate(self.credentials_path)
                self.app = initialize_app(cred)
            else:
                # Use environment variables or default credentials
                try:
                    self.app = initialize_app()
                except ValueError:
                    # If no app is initialized, try with default credentials
                    import firebase_admin
                    if not firebase_admin._apps:
                        # Try to initialize with default credentials
                        self.app = initialize_app()
            
            self.db = firestore.client()
            self._initialized = True
            print("✅ Firebase initialized successfully")
            
        except Exception as e:
            print(f"❌ Firebase initialization error: {e}")
            raise
    
    async def _ensure_initialized(self):
        """Ensure Firebase is initialized"""
        if not self._initialized:
            await self.init()
    
    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user in Firebase"""
        await self._ensure_initialized()
        
        try:
            # Add timestamp
            user_data['created_at'] = datetime.utcnow().isoformat()
            user_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Create document reference
            doc_ref = self.db.collection('users').document(str(user_data['tg_id']))
            doc_ref.set(user_data)
            
            return str(user_data['tg_id'])
            
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            raise
    
    async def get_user(self, tg_id: int) -> Optional[Dict[str, Any]]:
        """Get user by Telegram ID"""
        await self._ensure_initialized()
        
        try:
            doc_ref = self.db.collection('users').document(str(tg_id))
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
            
        except Exception as e:
            print(f"❌ Error getting user: {e}")
            return None
    
    async def update_user(self, tg_id: int, updates: Dict[str, Any]) -> bool:
        """Update user data"""
        await self._ensure_initialized()
        
        try:
            updates['updated_at'] = datetime.utcnow().isoformat()
            
            doc_ref = self.db.collection('users').document(str(tg_id))
            doc_ref.update(updates)
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating user: {e}")
            return False
    
    async def get_all_users(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all users with pagination"""
        await self._ensure_initialized()
        
        try:
            # Get users ordered by created_at
            query = self.db.collection('users').order_by('created_at', direction=BaseQuery.DESCENDING)
            
            if offset > 0:
                # Skip documents (Firebase doesn't have direct offset)
                # We'll need to implement pagination differently
                pass
            
            if limit > 0:
                query = query.limit(limit)
            
            docs = query.stream()
            users = []
            
            for doc in docs:
                user_data = doc.to_dict()
                user_data['tg_id'] = int(doc.id)  # Add tg_id from document ID
                users.append(user_data)
            
            return users
            
        except Exception as e:
            print(f"❌ Error getting all users: {e}")
            return []
    
    async def get_total_users_count(self) -> int:
        """Get total count of users"""
        await self._ensure_initialized()
        
        try:
            # Firebase doesn't have direct count, we need to count documents
            docs = self.db.collection('users').stream()
            count = sum(1 for _ in docs)
            return count
            
        except Exception as e:
            print(f"❌ Error getting user count: {e}")
            return 0
    
    async def search_users(self, search_term: str) -> List[Dict[str, Any]]:
        """Search users by name or phone"""
        await self._ensure_initialized()
        
        try:
            users = []
            
            # Search by full_name
            if search_term.isdigit():
                # Search by TG ID
                doc = self.db.collection('users').document(search_term).get()
                if doc.exists:
                    user_data = doc.to_dict()
                    user_data['tg_id'] = int(doc.id)
                    users.append(user_data)
            else:
                # Search by full_name or phone
                # Firebase doesn't support LIKE queries, so we need to get all and filter
                docs = self.db.collection('users').stream()
                
                for doc in docs:
                    user_data = doc.to_dict()
                    user_data['tg_id'] = int(doc.id)
                    
                    # Check if search term matches
                    full_name = user_data.get('full_name', '').lower()
                    phone = user_data.get('phone', '').lower()
                    search_term_lower = search_term.lower()
                    
                    if search_term_lower in full_name or search_term_lower in phone:
                        users.append(user_data)
            
            return users
            
        except Exception as e:
            print(f"❌ Error searching users: {e}")
            return []
    
    async def list_masters_by_profession(self, profession: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Get masters by profession"""
        await self._ensure_initialized()
        
        try:
            # Query for users with role 'usta' and matching profession
            query = (self.db.collection('users')
                    .where('role', '==', 'usta')
                    .where('profession', '==', profession)
                    .where('is_blocked', '==', False)
                    .order_by('created_at', direction=BaseQuery.DESCENDING))
            
            if limit > 0:
                query = query.limit(limit)
            
            docs = query.stream()
            masters = []
            
            for doc in docs:
                master_data = doc.to_dict()
                master_data['tg_id'] = int(doc.id)
                masters.append(master_data)
            
            return masters
            
        except Exception as e:
            print(f"❌ Error getting masters by profession: {e}")
            return []
    
    async def add_diamonds(self, tg_id: int, amount: int, reason: str = "") -> bool:
        """Add diamonds to user account"""
        await self._ensure_initialized()
        
        try:
            # Get current user
            user = await self.get_user(tg_id)
            if not user:
                return False
            
            current_diamonds = user.get('diamonds', 0)
            new_diamonds = current_diamonds + amount
            
            # Update user diamonds
            await self.update_user(tg_id, {
                'diamonds': new_diamonds
            })
            
            # Record transaction
            transaction_data = {
                'user_id': tg_id,
                'amount': amount,
                'reason': reason,
                'created_at': datetime.utcnow().isoformat()
            }
            
            self.db.collection('diamond_transactions').add(transaction_data)
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding diamonds: {e}")
            return False
    
    async def create_review(self, review_data: Dict[str, Any]) -> str:
        """Create a review"""
        await self._ensure_initialized()
        
        try:
            review_data['created_at'] = datetime.utcnow().isoformat()
            
            doc_ref = self.db.collection('reviews').add(review_data)
            return doc_ref[1].id  # Return document ID
            
        except Exception as e:
            print(f"❌ Error creating review: {e}")
            raise
    
    async def get_user_reviews(self, tg_id: int) -> List[Dict[str, Any]]:
        """Get reviews for a user"""
        await self._ensure_initialized()
        
        try:
            query = (self.db.collection('reviews')
                    .where('master_id', '==', tg_id)
                    .order_by('created_at', direction=BaseQuery.DESCENDING))
            
            docs = query.stream()
            reviews = []
            
            for doc in docs:
                review_data = doc.to_dict()
                review_data['id'] = doc.id
                reviews.append(review_data)
            
            return reviews
            
        except Exception as e:
            print(f"❌ Error getting reviews: {e}")
            return []
    
    async def create_chat(self, chat_data: Dict[str, Any]) -> str:
        """Create a chat session"""
        await self._ensure_initialized()
        
        try:
            chat_data['created_at'] = datetime.utcnow().isoformat()
            
            doc_ref = self.db.collection('chats').add(chat_data)
            return doc_ref[1].id
            
        except Exception as e:
            print(f"❌ Error creating chat: {e}")
            raise
    
    async def add_chat_message(self, chat_id: str, message_data: Dict[str, Any]) -> str:
        """Add message to chat"""
        await self._ensure_initialized()
        
        try:
            message_data['created_at'] = datetime.utcnow().isoformat()
            
            doc_ref = self.db.collection('chats').document(chat_id).collection('messages').add(message_data)
            return doc_ref[1].id
            
        except Exception as e:
            print(f"❌ Error adding chat message: {e}")
            raise
    
    async def get_chat_messages(self, chat_id: str) -> List[Dict[str, Any]]:
        """Get chat messages"""
        await self._ensure_initialized()
        
        try:
            query = (self.db.collection('chats').document(chat_id).collection('messages')
                    .order_by('created_at', direction=BaseQuery.ASCENDING))
            
            docs = query.stream()
            messages = []
            
            for doc in docs:
                message_data = doc.to_dict()
                message_data['id'] = doc.id
                messages.append(message_data)
            
            return messages
            
        except Exception as e:
            print(f"❌ Error getting chat messages: {e}")
            return []
    
    async def stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        await self._ensure_initialized()
        
        try:
            # Get total users
            total_users = await self.get_total_users_count()
            
            # Get total diamonds (need to sum all users' diamonds)
            users = await self.get_all_users(limit=1000)  # Get up to 1000 users
            total_balance = sum(user.get('diamonds', 0) for user in users)
            
            # Get total spent (sum negative transactions)
            transactions = self.db.collection('diamond_transactions').where('amount', '<', 0).stream()
            total_spent = sum(abs(doc.to_dict().get('amount', 0)) for doc in transactions)
            
            return {
                "total_users": total_users,
                "total_balance": total_balance,
                "total_spent": total_spent
            }
            
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            return {"total_users": 0, "total_balance": 0, "total_spent": 0}
    
    async def migrate_from_sqlite(self, sqlite_db_path: str):
        """Migrate data from SQLite to Firebase"""
        await self._ensure_initialized()
        
        try:
            from db import Database as SQLiteDatabase
            
            sqlite_db = SQLiteDatabase(sqlite_db_path)
            await sqlite_db.init()
            
            print("🔄 Starting migration from SQLite to Firebase...")
            
            # Migrate users
            sqlite_users = await sqlite_db.get_all_users(limit=1000)
            migrated_count = 0
            
            for user in sqlite_users:
                # Convert user data
                firebase_user = {
                    'tg_id': user.get('tg_id'),
                    'full_name': user.get('full_name'),
                    'phone': user.get('phone'),
                    'email': user.get('email'),
                    'region': user.get('region'),
                    'purpose': user.get('purpose'),
                    'role': user.get('role'),
                    'diamonds': user.get('diamonds', 0),
                    'diamonds_spent': user.get('diamonds_spent', 0),
                    'top_until': user.get('top_until'),
                    'vip_until': user.get('vip_until'),
                    'is_blocked': user.get('is_blocked', 0),
                    'last_seen': user.get('last_seen'),
                    'profession': user.get('profession'),
                    'bio': user.get('bio'),
                    'photo_id': user.get('photo_id'),
                    'ref_code': user.get('ref_code'),
                    'referred_by': user.get('referred_by')
                }
                
                await self.create_user(firebase_user)
                migrated_count += 1
                
                if migrated_count % 10 == 0:
                    print(f"📊 Migrated {migrated_count} users...")
            
            print(f"✅ Migration completed! Migrated {migrated_count} users to Firebase")
            
        except Exception as e:
            print(f"❌ Migration error: {e}")
            raise

# Firebase configuration
def get_firebase_config():
    """Get Firebase configuration from environment or file"""
    firebase_config = {
        "type": os.getenv("FIREBASE_TYPE"),
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n") if os.getenv("FIREBASE_PRIVATE_KEY") else None,
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
        "token_uri": os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
        "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs"),
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
    }
    
    # Remove None values
    firebase_config = {k: v for k, v in firebase_config.items() if v is not None}
    
    return firebase_config

# Initialize Firebase database instance
firebase_db = FirebaseDB()
