#!/usr/bin/env python3
"""
Test script for the new quotation chat messages endpoint
GET /api/<quotation_id>/chat-messages/<insurer_id>
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"  # Change this to your server URL
AUTH_TOKEN = "your_auth_token_here"  # Replace with actual token

def test_quotation_chat_messages(quotation_id, insurer_id, sync_thread=False):
    """Test the quotation chat messages endpoint"""
    print(f"\n=== Testing: Quotation Chat Messages ===")
    print(f"Quotation ID: {quotation_id}")
    print(f"Insurer ID: {insurer_id}")
    print(f"Sync Thread: {sync_thread}")
    
    # Build URL
    url = f"{BASE_URL}/api/{quotation_id}/chat-messages/{insurer_id}"
    
    # Add query parameters
    params = {}
    if sync_thread:
        params['sync_thread'] = 'true'
    
    # Headers
    headers = {
        'Authorization': f'Bearer {AUTH_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"Request URL: {url}")
        print(f"Parameters: {params}")
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Check if conversation metadata is present
            if data.get('success') and data.get('data', {}).get('conversation_metadata'):
                metadata = data['data']['conversation_metadata']
                print(f"\n📋 Conversation Metadata:")
                print(f"  Conversation ID: {metadata.get('conversation_id')}")
                print(f"  Conversation Code: {metadata.get('conversation_code')}")
                print(f"  Type: {metadata.get('type')}")
                print(f"  Quotation ID: {metadata.get('quotation_id')}")
                print(f"  Insurer ID: {metadata.get('insurer_id')}")
                print(f"  Type Based ID: {metadata.get('type_based_id')}")
            
            # Check messages
            messages = data.get('data', {}).get('messages', [])
            print(f"\n💬 Messages Found: {len(messages)}")
            
            # Check pagination
            pagination = data.get('data', {}).get('pagination', {})
            if pagination:
                print(f"\n📄 Pagination:")
                print(f"  Page: {pagination.get('page')}")
                print(f"  Page Size: {pagination.get('page_size')}")
                print(f"  Total Count: {pagination.get('total_count')}")
                print(f"  Total Pages: {pagination.get('total_pages')}")
                
        else:
            print("❌ Error!")
            try:
                error_data = response.json()
                print(f"Error Response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error Text: {response.text}")
                
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

def test_not_found_scenario():
    """Test with non-existent quotation/insurer combination"""
    print(f"\n=== Testing: Not Found Scenario ===")
    test_quotation_chat_messages(99999, 99999)

def main():
    """Run all tests"""
    print("🧪 Testing Quotation Chat Messages Endpoint")
    print("=" * 50)
    
    # Test with real data (replace with actual values)
    test_quotation_chat_messages(123, 456)
    
    # Test with Gmail sync
    test_quotation_chat_messages(123, 456, sync_thread=True)
    
    # Test not found scenario
    test_not_found_scenario()
    
    print(f"\n✅ All tests completed!")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        # Allow command line usage: python test_quotation_chat_messages.py <quotation_id> <insurer_id>
        quotation_id = int(sys.argv[1])
        insurer_id = int(sys.argv[2])
        sync_thread = len(sys.argv) > 3 and sys.argv[3].lower() == 'true'
        test_quotation_chat_messages(quotation_id, insurer_id, sync_thread)
    else:
        main()
