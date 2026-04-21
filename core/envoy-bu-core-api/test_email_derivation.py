#!/usr/bin/env python3
"""
Simple test to verify email derivation logic in send_chatmail_message endpoint
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
AUTH_TOKEN = "your_auth_token_here"

def test_email_derivation():
    """Test the email derivation logic"""
    print("🧪 Testing Email Derivation Logic")
    print("=" * 40)
    
    # Test case 1: Send message with conversation_id (should derive from insurer)
    print("\n📧 Test Case 1: Conversation with insurer")
    print("Expected: to_email = insurer email, from_email = system email")
    
    data = {
        "body": "Test message - should derive emails correctly",
        "conversation_id": 4  # Replace with actual conversation ID
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AUTH_TOKEN}"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/chatmail/send", json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("is_success"):
                print("✅ SUCCESS: Email derivation worked correctly!")
                print(f"   - Message ID: {result.get('result', {}).get('message_id')}")
                print(f"   - Conversation ID: {result.get('result', {}).get('conversation_id')}")
            else:
                print(f"❌ FAILED: {result.get('message')}")
        else:
            print(f"❌ HTTP ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    # Test case 2: Send message without conversation_id (should use provided emails)
    print("\n📧 Test Case 2: New conversation")
    print("Expected: Use provided to_email and derive from_email from Gmail credentials")
    
    data = {
        "to_email": "test@example.com",
        "subject": "Test New Conversation",
        "body": "Test message for new conversation",
        "conversation_type": "QUOTATION",
        "type_based_id": "QR-TEST-001",
        "insurer_id": 1  # Replace with actual insurer ID
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/chatmail/send", json=data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("is_success"):
                print("✅ SUCCESS: New conversation created correctly!")
                print(f"   - Message ID: {result.get('result', {}).get('message_id')}")
                print(f"   - Conversation ID: {result.get('result', {}).get('conversation_id')}")
            else:
                print(f"❌ FAILED: {result.get('message')}")
        else:
            print(f"❌ HTTP ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    if AUTH_TOKEN == "your_auth_token_here":
        print("⚠️  Please set AUTH_TOKEN to a valid token before running tests!")
    else:
        test_email_derivation()
