# 🔥 Firebase Integration Setup Guide

## 📋 Overview
This guide explains how to set up Firebase integration for the Usta Top Bot project.

## 🚀 Quick Setup

### 1. Firebase Project Setup
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or use existing "zinox-usta-bot"
3. Enable Firestore Database
4. Create a service account key

### 2. Service Account Configuration
1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate new private key"
3. Download the JSON file
4. Copy the contents to your environment variables or firebase_credentials.json

### 3. Environment Variables
Add these to your `.env` file:

```bash
# Firebase Configuration
DB_TYPE=firebase
FIREBASE_PROJECT_ID=zinox-usta-bot
FIREBASE_PRIVATE_KEY_ID=your_private_key_id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@zinox-usta-bot.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your_client_id
FIREBASE_TYPE=service_account
```

### 4. Install Dependencies
```bash
pip install firebase-admin google-cloud-firestore
```

## 📊 Firebase Collections Structure

### Users Collection
```
users/{tg_id}
├── tg_id: 123456789
├── full_name: "John Doe"
├── phone: "+998901234567"
├── email: "john@example.com"
├── region: "Toshkent"
├── purpose: "usta"
├── role: "usta|mijoz"
├── diamonds: 100
├── diamonds_spent: 50
├── top_until: "2024-12-31T23:59:59"
├── vip_until: "2024-12-31T23:59:59"
├── is_blocked: 0|1
├── last_seen: "2024-01-01T12:00:00"
├── profession: "electrician"
├── bio: "Professional electrician"
├── photo_id: "photo_file_id"
├── ref_code: "ref123"
├── referred_by: 123456788
├── created_at: "2024-01-01T00:00:00"
└── updated_at: "2024-01-01T00:00:00"
```

### Reviews Collection
```
reviews/{review_id}
├── user_id: 123456789
├── master_id: 987654321
├── rating: 5
├── comment: "Great service!"
├── created_at: "2024-01-01T00:00:00"
```

### Chats Collection
```
chats/{chat_id}
├── client_id: 123456789
├── master_id: 987654321
├── status: "active|closed"
├── created_at: "2024-01-01T00:00:00"
└── messages/{message_id}
    ├── sender_id: 123456789
    ├── text: "Hello!"
    ├── created_at: "2024-01-01T00:00:00"
```

### Diamond Transactions Collection
```
diamond_transactions/{transaction_id}
├── user_id: 123456789
├── amount: 10
├── reason: "purchase"
├── created_at: "2024-01-01T00:00:00"
```

## 🔧 Database Factory

The bot now supports both SQLite and Firebase databases through a factory pattern:

```python
from db_factory import get_database

# Automatically chooses based on DB_TYPE environment variable
db = get_database()
await db.init()
```

## 📝 Migration from SQLite to Firebase

### Automatic Migration
```python
from firebase_db import FirebaseDB

firebase_db = FirebaseDB()
await firebase_db.migrate_from_sqlite("ustaqidir.db")
```

### Manual Migration Steps
1. Set up Firebase project
2. Configure environment variables
3. Run migration script
4. Test all functionality

## 🧪 Testing Firebase Integration

### Test Script
```python
python test_firebase.py
```

### Manual Testing
1. Create test user
2. Verify user creation
3. Test user updates
4. Test search functionality
5. Verify analytics

## 🔒 Security Considerations

### Service Account Security
- Never commit service account keys to version control
- Use environment variables in production
- Rotate keys regularly
- Limit service account permissions

### Firebase Security Rules
```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Admins can read all data
    match /{document=**} {
      allow read, write: if request.auth != null && 
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.role == 'admin';
    }
  }
}
```

## 📊 Benefits of Firebase Integration

### ✅ Advantages
- **Scalability**: Automatic scaling with Google infrastructure
- **Real-time Updates**: Real-time data synchronization
- **Offline Support**: Built-in offline caching
- **Security**: Google's security infrastructure
- **Analytics**: Built-in analytics and monitoring
- **Global CDN**: Fast data access worldwide

### ⚠️ Considerations
- **Cost**: Firebase has usage-based pricing
- **Learning Curve**: Different query syntax than SQL
- **Latency**: Slightly higher latency than local SQLite
- **Dependencies**: Additional dependencies required

## 🚀 Deployment

### Development
```bash
DB_TYPE=sqlite  # Use SQLite for development
```

### Production
```bash
DB_TYPE=firebase  # Use Firebase for production
```

### Environment Setup
1. Development: SQLite (fast, local)
2. Staging: Firebase (test with real data)
3. Production: Firebase (scalable, reliable)

## 📞 Support

### Common Issues
1. **Authentication Errors**: Check service account configuration
2. **Permission Errors**: Verify Firestore rules
3. **Connection Issues**: Check network connectivity
4. **Data Loss**: Always backup before migration

### Debug Tips
- Use Firebase Console to verify data
- Check logs for detailed error messages
- Test with small datasets first
- Monitor usage and costs

## 🔄 Backup and Recovery

### Firebase Backup
```python
# Export data
firebase firestore export gs://your-bucket/backup-path

# Import data
firebase firestore import gs://your-bucket/backup-path
```

### Regular Backups
- Schedule daily exports
- Store backups in multiple locations
- Test restore procedures regularly

---

**🔥 Firebase integration provides scalable, reliable database solution for Usta Top Bot!**
