#!/usr/bin/env python3
"""
Test script for the new quotation sync conversations endpoint
POST /api/<quotation_id>/sync-conversations
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000"  # Change this to your server URL
AUTH_TOKEN = "your_auth_token_here"  # Replace with actual token

def test_quotation_sync_conversations(quotation_id):
    """Test the quotation sync conversations endpoint"""
    print(f"\n=== Testing: Quotation Sync Conversations ===")
    print(f"Quotation ID: {quotation_id}")
    
    # Build URL
    url = f"{BASE_URL}/api/{quotation_id}/sync-conversations"
    
    # Headers
    headers = {
        'Authorization': f'Bearer {AUTH_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"Request URL: {url}")
        print(f"Method: POST")
        
        response = requests.post(url, headers=headers, timeout=120)  # Longer timeout for sync operations
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success!")
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Check sync results
            if data.get('success') and data.get('data'):
                sync_data = data['data']
                print(f"\n📊 Sync Summary:")
                print(f"  Total Conversations: {sync_data.get('total_conversations')}")
                print(f"  Successful Syncs: {sync_data.get('successful_syncs')}")
                print(f"  Failed Syncs: {sync_data.get('failed_syncs')}")
                
                # Check individual results
                sync_results = sync_data.get('sync_results', [])
                if sync_results:
                    print(f"\n📋 Individual Results:")
                    for i, result in enumerate(sync_results, 1):
                        status_icon = "✅" if result.get('status') == 'success' else "❌"
                        print(f"  {i}. {status_icon} Conversation {result.get('conversation_id')} (Insurer: {result.get('insurer_id')})")
                        print(f"     Status: {result.get('status')}")
                        if result.get('error'):
                            print(f"     Error: {result.get('error')}")
                        if result.get('response'):
                            print(f"     Response: {json.dumps(result.get('response'), indent=4)}")
                
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
    """Test with non-existent quotation"""
    print(f"\n=== Testing: Not Found Scenario ===")
    test_quotation_sync_conversations(99999)

def main():
    """Run all tests"""
    print("🧪 Testing Quotation Sync Conversations Endpoint")
    print("=" * 50)
    
    # Test with real data (replace with actual values)
    test_quotation_sync_conversations(123)
    
    # Test not found scenario
    test_not_found_scenario()
    
    print(f"\n✅ All tests completed!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Allow command line usage: python test_quotation_sync_conversations.py <quotation_id>
        quotation_id = int(sys.argv[1])
        test_quotation_sync_conversations(quotation_id)
    else:
        main()
