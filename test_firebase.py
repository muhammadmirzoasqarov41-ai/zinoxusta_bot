#!/usr/bin/env python3
"""
Test Firebase integration for Usta Top Bot
"""

import asyncio
import os
from firebase_db import FirebaseDB
from config import load_config

async def test_firebase():
    print("🔥 Testing Firebase integration...")
    
    # Test Firebase initialization
    try:
        firebase_db = FirebaseDB()
        await firebase_db.init()
        print("✅ Firebase initialized successfully")
    except Exception as e:
        print(f"❌ Firebase initialization failed: {e}")
        return
    
    # Test creating a user
    try:
        test_user = {
            'tg_id': 123456789,
            'full_name': 'Test User',
            'phone': '+998901234567',
            'region': 'Toshkent',
            'role': 'mijoz',
            'diamonds': 10,
            'is_blocked': 0
        }
        
        user_id = await firebase_db.create_user(test_user)
        print(f"✅ User created successfully: {user_id}")
    except Exception as e:
        print(f"❌ User creation failed: {e}")
        return
    
    # Test getting user
    try:
        user = await firebase_db.get_user(123456789)
        if user:
            print(f"✅ User retrieved successfully: {user['full_name']}")
        else:
            print("❌ User not found")
    except Exception as e:
        print(f"❌ User retrieval failed: {e}")
    
    # Test updating user
    try:
        success = await firebase_db.update_user(123456789, {'diamonds': 15})
        if success:
            print("✅ User updated successfully")
        else:
            print("❌ User update failed")
    except Exception as e:
        print(f"❌ User update failed: {e}")
    
    # Test getting all users
    try:
        users = await firebase_db.get_all_users(limit=5)
        print(f"✅ Retrieved {len(users)} users")
    except Exception as e:
        print(f"❌ Getting all users failed: {e}")
    
    # Test search
    try:
        search_results = await firebase_db.search_users("Test")
        print(f"✅ Search completed: {len(search_results)} results")
    except Exception as e:
        print(f"❌ Search failed: {e}")
    
    # Test stats
    try:
        stats = await firebase_db.stats()
        print(f"✅ Stats retrieved: {stats}")
    except Exception as e:
        print(f"❌ Stats retrieval failed: {e}")
    
    # Clean up test user
    try:
        # In Firebase, we need to delete the document
        if firebase_db.db:
            firebase_db.db.collection('users').document('123456789').delete()
            print("✅ Test user cleaned up")
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
    
    print("\n🎉 Firebase integration test completed!")

if __name__ == "__main__":
    asyncio.run(test_firebase())
