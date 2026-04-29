#!/usr/bin/env python3
"""
Firebase Credentials Setup Helper
This script helps set up Firebase credentials for the Usta Top Bot
"""

import os
import json
from pathlib import Path

def create_firebase_credentials():
    """
    Create Firebase credentials file from environment variables
    """
    print("🔥 Setting up Firebase credentials...")
    
    # Get Firebase configuration from environment
    firebase_config = {
        "type": os.getenv("FIREBASE_TYPE", "service_account"),
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n") if os.getenv("FIREBASE_PRIVATE_KEY") else None,
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
        "token_uri": os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
        "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL", "https://www.googleapis.com/oauth2/v1/certs"),
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
    }
    
    # Remove None values
    firebase_config = {k: v for k, v in firebase_config.items() if v is not None}
    
    # Check if required fields are present
    required_fields = ["project_id", "private_key", "client_email"]
    missing_fields = [field for field in required_fields if not firebase_config.get(field)]
    
    if missing_fields:
        print(f"❌ Missing required Firebase configuration: {', '.join(missing_fields)}")
        print("\n📋 Please set these environment variables:")
        for field in missing_fields:
            print(f"   FIREBASE_{field.upper()}")
        
        print("\n🔗 Get credentials from: https://console.firebase.google.com/")
        print("   1. Go to Project Settings → Service Accounts")
        print("   2. Click 'Generate new private key'")
        print("   3. Download and copy the values")
        
        return False
    
    # Create credentials file
    credentials_path = Path("firebase_credentials.json")
    
    try:
        with open(credentials_path, 'w', encoding='utf-8') as f:
            json.dump(firebase_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Firebase credentials saved to: {credentials_path}")
        print("🔐 Credentials file created successfully!")
        
        # Verify the file was created
        if credentials_path.exists():
            print(f"📁 File size: {credentials_path.stat().st_size} bytes")
            return True
        else:
            print("❌ Credentials file was not created")
            return False
            
    except Exception as e:
        print(f"❌ Error creating credentials file: {e}")
        return False

def show_firebase_setup_guide():
    """Show detailed Firebase setup guide"""
    print("""
🔥 FIREBASE SETUP GUIDE
==================

1. CREATE FIREBASE PROJECT:
   • Go to https://console.firebase.google.com/
   • Click "Add project"
   • Enter project name: "zinox-usta-bot"
   • Enable Google Analytics (optional)
   • Click "Create project"

2. SET UP FIRESTORE DATABASE:
   • Go to "Build" → "Firestore Database"
   • Click "Create database"
   • Choose "Start in test mode" (for testing)
   • Select a location (choose closest to your users)

3. CREATE SERVICE ACCOUNT:
   • Go to "Project Settings" → "Service accounts"
   • Click "Generate new private key"
   • Select "JSON" format
   • Download the file

4. CONFIGURE ENVIRONMENT VARIABLES:
   Add these to your .env file:
   
   DB_TYPE=firebase
   FIREBASE_PROJECT_ID=zinox-usta-bot
   FIREBASE_PRIVATE_KEY_ID=your_private_key_id
   FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\\nYOUR_KEY_HERE\\n-----END PRIVATE KEY-----"
   FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@zinox-usta-bot.iam.gserviceaccount.com
   FIREBASE_CLIENT_ID=your_client_id
   FIREBASE_TYPE=service_account

5. RUN SETUP SCRIPT:
   python setup_firebase_credentials.py

6. TEST INTEGRATION:
   python test_firebase.py

🔗 Useful Links:
• Firebase Console: https://console.firebase.google.com/
• Firestore Docs: https://firebase.google.com/docs/firestore
• Admin SDK: https://firebase.google.com/docs/admin/setup

💡 Tips:
• Keep your private key secure!
• Don't commit credentials to git
• Use environment variables in production
• Test with small datasets first
""")

def main():
    """Main setup function"""
    print("🔥 Usta Top Bot - Firebase Setup")
    print("=" * 40)
    
    # Check if Firebase is already configured
    if os.getenv("FIREBASE_PROJECT_ID") and os.getenv("FIREBASE_PRIVATE_KEY"):
        print("📋 Firebase configuration found in environment variables")
        
        choice = input("\nDo you want to create credentials file? (y/n): ").lower()
        if choice == 'y':
            success = create_firebase_credentials()
            if success:
                print("\n✅ Firebase setup completed!")
                print("🧪 Run 'python test_firebase.py' to test the integration")
            else:
                print("\n❌ Firebase setup failed!")
        else:
            print("\nℹ️ Skipping credentials file creation")
    else:
        print("❌ Firebase configuration not found")
        show_firebase_setup_guide()
        
        choice = input("\nDo you want to see the setup guide again? (y/n): ").lower()
        if choice == 'y':
            show_firebase_setup_guide()

if __name__ == "__main__":
    main()
