#!/usr/bin/env python3
"""
Test script for the new /api/send-message endpoint
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust this to your Django server URL
API_ENDPOINT = f"{BASE_URL}/api/send-message"

# Test data
test_payload = {
    "body": "This is a test message from the new send-message endpoint",
    "subject": "Test Subject - Envoy Integration",
    "to_mail": "recipient@example.com",
    "thread_id": "optional_thread_id_for_replies",
    "from_email": "sender@example.com",
    "idp_access_token": "your_idp_access_token_here"  # Replace with actual token
}

def test_send_message_endpoint():
    """Test the send-message endpoint"""
    
    print("Testing /api/send-message endpoint...")
    print(f"Endpoint: {API_ENDPOINT}")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    print("-" * 50)
    
    try:
        # Note: You'll need to add authentication headers here
        # For testing, you might need to get a valid token first
        headers = {
            "Content-Type": "application/json",
            # "Authorization": "Bearer YOUR_TOKEN_HERE"  # Add your auth token
        }
        
        response = requests.post(
            API_ENDPOINT,
            json=test_payload,
            headers=headers,
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        response_data = response.json()
        print(f"Response Body: {json.dumps(response_data, indent=2)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Endpoint is working correctly!")
            data = response_data.get('data', {})
            print(f"Conversation ID: {data.get('conversation_id')}")
            print(f"First Message ID: {data.get('first_message_id')}")
            print(f"Conversation Code: {data.get('conversation_code')}")
            print(f"Gmail Message ID: {data.get('gmail_message_id')}")
            print(f"Gmail Thread ID: {data.get('gmail_thread_id')}")
            print(f"Sent At: {data.get('sent_at')}")
            print(f"Thread ID: {data.get('thread_id')}")
        else:
            print("❌ FAILED: Endpoint returned an error")
            print(f"Error: {response_data.get('error', 'Unknown error')}")
            print(f"Error Code: {response_data.get('error_code', 'N/A')}")
            print(f"Message: {response_data.get('message', 'No message provided')}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Request failed - {str(e)}")
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON response - {str(e)}")
        print(f"Raw response: {response.text}")
    except Exception as e:
        print(f"❌ ERROR: Unexpected error - {str(e)}")

def test_without_auth():
    """Test without authentication to see the auth error"""
    print("\nTesting without authentication...")
    print("-" * 50)
    
    try:
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(
            API_ENDPOINT,
            json=test_payload,
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING NEW SEND-MESSAGE ENDPOINT")
    print("=" * 60)
    
    # Test without auth first
    test_without_auth()
    
    # Test with auth (you'll need to add your token)
    # test_send_message_endpoint()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)
