#!/usr/bin/env python3
"""
Test script for the updated quotation approval email functionality
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust this to your Django server URL

def test_quotation_approval_changes():
    """Test the quotation approval changes endpoint with email sending"""
    
    print("Testing quotation approval changes with email sending...")
    
    # Test data for quotation approval changes
    approval_payload = {
        "status": "approved",
        "remarks": "Approved after review"
        # Note: idp_access_token is now automatically extracted from Authorization header
    }
    
    # Replace with actual approval ID
    approval_id = 1
    
    url = f"{BASE_URL}/api/approvals/{approval_id}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_JWT_TOKEN'  # Replace with actual JWT token
    }
    
    print(f"Endpoint: {url}")
    print(f"Payload: {json.dumps(approval_payload, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.put(url, json=approval_payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_quotation_approval_send_email():
    """Test the quotation approval send email endpoint directly"""
    
    print("\nTesting quotation approval send email endpoint...")
    
    # Test data for sending email
    email_payload = {
        "service_provider_ids": [1, 2, 3],  # Replace with actual service provider IDs
        "subject": "Quotation Approval - Test Subject",
        "body": "This is a test email body for quotation approval. The quotation has been approved and is ready for processing."
        # Note: idp_access_token is now automatically extracted from Authorization header
    }
    
    url = f"{BASE_URL}/api/approvals/send-email"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_JWT_TOKEN'  # Replace with actual JWT token
    }
    
    print(f"Endpoint: {url}")
    print(f"Payload: {json.dumps(email_payload, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=email_payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {str(e)}")

def test_send_message_api():
    """Test the send-message API directly"""
    
    print("\nTesting send-message API directly...")
    
    # Test data for send-message API
    send_message_payload = {
        "body": "This is a test message from the send-message API",
        "subject": "Test Subject - Send Message API",
        "to_mail": "recipient@example.com",  # Replace with actual recipient email
        "from_email": "sender@example.com",  # Replace with actual sender email
        "idp_access_token": "your_idp_access_token_here",  # Replace with actual token
        "conversation_id": ""  # Empty for new conversations
    }
    
    url = f"{BASE_URL}/api/send-message"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_JWT_TOKEN'  # Replace with actual JWT token
    }
    
    print(f"Endpoint: {url}")
    print(f"Payload: {json.dumps(send_message_payload, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=send_message_payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Quotation Approval Email Testing")
    print("=" * 50)
    
    # Test the send-message API first
    test_send_message_api()
    
    # Test the quotation approval send email endpoint
    test_quotation_approval_send_email()
    
    # Test the full quotation approval changes flow
    test_quotation_approval_changes()
    
    print("\n" + "=" * 50)
    print("Testing completed!")
    print("\nNotes:")
    print("1. The JWT token from Authorization header is automatically used as IDP access token")
    print("2. Replace 'YOUR_JWT_TOKEN' with actual JWT token")
    print("3. Replace service provider IDs with actual IDs from your database")
    print("4. Replace email addresses with actual email addresses")
    print("5. Replace approval_id with actual approval ID from your database")
    print("6. For send-message API, you still need to provide idp_access_token in the payload")
