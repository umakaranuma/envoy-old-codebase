#!/usr/bin/env python3
"""
Test script for Chatmail functionality
Demonstrates sending new messages and replies using the new chatmail endpoints
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust to your Django server URL
API_TOKEN = "your_auth_token_here"  # Replace with actual auth token

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def test_send_new_message():
    """Test sending a new chatmail message (creates new conversation)"""
    print("=== Testing: Send New Message ===")
    
    payload = {
        "to_email": "recipient@example.com",
        "from_email": "sender@yourcompany.com",
        "subject": "New Quotation Request",
        "body": "Hello, I would like to request a quotation for motor insurance.",
        "conversation_type": "QUOTATION",
        "type_based_id": "QR-2024-001",
        "insurer_id": 1,  # ServiceProvider ID
        "attachments": [
            {
                "file_name": "document.pdf",
                "file_url": "https://example.com/files/document.pdf",
                "content_type": "application/pdf",
                "size_bytes": 1024000,
                "is_image": False
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/chatmail/send",
        headers=headers,
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        data = response.json()
        return data.get('data', {}).get('conversation_id')
    return None

def test_send_reply_message(conversation_id):
    """Test sending a reply message to existing conversation"""
    print(f"\n=== Testing: Send Reply to Conversation {conversation_id} ===")
    
    payload = {
        "to_email": "recipient@example.com",
        "from_email": "sender@yourcompany.com",
        "subject": "Re: New Quotation Request",
        "body": "Thank you for your request. I have attached the quotation details.",
        "conversation_id": conversation_id,
        "attachments": [
            {
                "file_name": "quotation.pdf",
                "file_url": "https://example.com/files/quotation.pdf",
                "content_type": "application/pdf",
                "size_bytes": 2048000,
                "is_image": False
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/api/chatmail/send",
        headers=headers,
        json=payload
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_get_conversations():
    """Test getting all conversations"""
    print("\n=== Testing: Get Conversations ===")
    
    response = requests.get(
        f"{BASE_URL}/api/chatmail/conversations",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_get_messages(conversation_id=None):
    """Test getting messages with optional conversation filter"""
    print(f"\n=== Testing: Get Messages ===")
    
    url = f"{BASE_URL}/api/chatmail/messages"
    if conversation_id:
        url += f"?conversation_id={conversation_id}"
    
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def main():
    """Run all tests"""
    print("🚀 Starting Chatmail Functionality Tests\n")
    
    # Test 1: Send new message
    conversation_id = test_send_new_message()
    
    if conversation_id:
        # Test 2: Send reply to the conversation
        test_send_reply_message(conversation_id)
        
        # Test 3: Get all conversations
        test_get_conversations()
        
        # Test 4: Get messages for specific conversation
        test_get_messages(conversation_id)
        
        # Test 5: Get all messages
        test_get_messages()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()
