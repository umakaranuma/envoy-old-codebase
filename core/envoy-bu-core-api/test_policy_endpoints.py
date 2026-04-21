#!/usr/bin/env python3
"""
Test script for the new policy endpoints
GET /api/<policy_id>/chat-messages
POST /api/<policy_id>/sync-conversations
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"  # Change this to your server URL
AUTH_TOKEN = "your_auth_token_here"  # Replace with actual token

def test_policy_chat_messages(policy_id, sync_thread=False):
    """Test the policy chat messages endpoint"""
    print(f"\n=== Testing: Policy Chat Messages ===")
    print(f"Policy ID: {policy_id}")
    print(f"Sync Thread: {sync_thread}")
    
    # Build URL
    url = f"{BASE_URL}/api/{policy_id}/chat-messages"
    
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
        print(f"Method: GET")
        print(f"Headers: {headers}")
        print(f"Params: {params}")
        
        # Make the request
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"Response Data: {json.dumps(data, indent=2)}")
            
            # Extract key information
            if 'data' in data:
                messages = data['data'].get('data', [])
                pagination = data['data'].get('pagination', {})
                conversation_metadata = data['data'].get('conversation_metadata', {})
                
                print(f"\n📊 Summary:")
                print(f"  - Total messages: {len(messages)}")
                print(f"  - Conversation ID: {conversation_metadata.get('conversation_id')}")
                print(f"  - Type Based ID: {conversation_metadata.get('type_based_id')}")
                print(f"  - Policy ID: {conversation_metadata.get('policy_id')}")
                print(f"  - Insurer ID: {conversation_metadata.get('insurer_id')}")
                
                if messages:
                    print(f"\n📧 Sample Message:")
                    sample_msg = messages[0]
                    print(f"  - ID: {sample_msg.get('id')}")
                    print(f"  - Subject: {sample_msg.get('subject')}")
                    print(f"  - From: {sample_msg.get('from_email')}")
                    print(f"  - Type: {sample_msg.get('type')}")
                    print(f"  - Attachments: {len(sample_msg.get('attachments', []))}")
        else:
            print(f"❌ Error!")
            print(f"Response Text: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

def test_policy_sync_conversations(policy_id):
    """Test the policy sync conversations endpoint"""
    print(f"\n=== Testing: Policy Sync Conversations ===")
    print(f"Policy ID: {policy_id}")
    
    # Build URL
    url = f"{BASE_URL}/api/{policy_id}/sync-conversations"
    
    # Headers
    headers = {
        'Authorization': f'Bearer {AUTH_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"Request URL: {url}")
        print(f"Method: POST")
        print(f"Headers: {headers}")
        
        # Make the request
        response = requests.post(url, headers=headers, timeout=60)  # Longer timeout for sync operations
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"Response Data: {json.dumps(data, indent=2)}")
            
            # Extract key information
            if 'data' in data:
                total_conversations = data['data'].get('total_conversations', 0)
                successful_syncs = data['data'].get('successful_syncs', 0)
                failed_syncs = data['data'].get('failed_syncs', 0)
                sync_results = data['data'].get('sync_results', [])
                
                print(f"\n📊 Summary:")
                print(f"  - Total conversations: {total_conversations}")
                print(f"  - Successful syncs: {successful_syncs}")
                print(f"  - Failed syncs: {failed_syncs}")
                print(f"  - Type Based ID: {data['data'].get('type_based_id')}")
                
                if sync_results:
                    print(f"\n🔄 Sync Results:")
                    for i, result in enumerate(sync_results[:3]):  # Show first 3 results
                        print(f"  {i+1}. Conversation {result.get('conversation_id')} ({result.get('insurer_id')}): {result.get('status')}")
                        if result.get('status') == 'failed':
                            print(f"     Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ Error!")
            print(f"Response Text: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")

def main():
    """Main test function"""
    print("🚀 Policy Endpoints Test Script")
    print("=" * 50)
    
    # Test parameters - modify these as needed
    policy_id = 123  # Replace with actual policy ID
    
    print(f"Test Configuration:")
    print(f"  - Base URL: {BASE_URL}")
    print(f"  - Policy ID: {policy_id}")
    print(f"  - Auth Token: {'Set' if AUTH_TOKEN != 'your_auth_token_here' else 'NOT SET'}")
    
    if AUTH_TOKEN == "your_auth_token_here":
        print("\n⚠️  WARNING: Please set AUTH_TOKEN to a valid token before running tests!")
        return
    
    # Test 1: Get policy chat messages (database only)
    test_policy_chat_messages(policy_id, sync_thread=False)
    
    # Test 2: Get policy chat messages with Gmail sync
    test_policy_chat_messages(policy_id, sync_thread=True)
    
    # Test 3: Sync all conversations for the policy
    test_policy_sync_conversations(policy_id)
    
    print(f"\n✅ All tests completed!")

if __name__ == "__main__":
    main()
