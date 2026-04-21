#!/usr/bin/env python3
"""
Test script to verify quotation approval email document CDN processing functionality
"""

import os
import sys
import json

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set environment variables for testing
os.environ.setdefault('CDN_BASE_URL', 'https://cdn.example.com')

def test_approval_email_document_processing():
    """Test the quotation approval email document processing functionality"""
    
    # Import the service
    from envoy_bu_crm_api.quotation.services.document_cdn_service import DocumentCDNService
    
    # Test data similar to the user's payload for approval email
    test_documents = [
        {
            "name": "1eJCkMykAMlSF4P71AKt6_html_export_10.pdf",
            "doc": "quotation/1eJCkMykAMlSF4P71AKt6_html_export_10.pdf"
        },
        {
            "name": "UYjawrx8xsUnzUwzTwovm_html_export_51.pdf",
            "doc": "quotation/UYjawrx8xsUnzUwzTwovm_html_export_51.pdf"
        },
        {
            "doc": "envoy-test/a8E-14qoyFBMCBA8xcgfT_html_export_5.pdf",
            "name": "html_export_5.pdf",
            "type": "pdf"
        }
    ]
    
    print("Testing Quotation Approval Email Document Processing...")
    print("Input documents:")
    print(json.dumps(test_documents, indent=2))
    
    # Process documents
    cdn_links = DocumentCDNService.process_documents_for_email(test_documents)
    
    print("\nGenerated CDN links:")
    for i, link in enumerate(cdn_links, 1):
        print(f"{i}. {link}")
    
    # Simulate the approval email processing logic
    links = []  # Legacy links
    documents = test_documents
    
    # Process documents array to get CDN URLs from doc field
    document_cdn_links = DocumentCDNService.process_documents_for_email(documents)
    
    # Also handle legacy document_link field for backward compatibility
    for doc in documents:
        if isinstance(doc, dict) and doc.get("document_link"):
            links.append(doc["document_link"])
    
    # Combine all links
    all_links = links + document_cdn_links
    
    print(f"\nLegacy links: {len(links)}")
    for i, link in enumerate(links, 1):
        print(f"  {i}. {link}")
    
    print(f"\nDocument CDN links: {len(document_cdn_links)}")
    for i, link in enumerate(document_cdn_links, 1):
        print(f"  {i}. {link}")
    
    print(f"\nCombined all_links ({len(all_links)} total):")
    for i, link in enumerate(all_links, 1):
        print(f"  {i}. {link}")
    
    # Simulate email payload
    recipient_emails = ["provider1@example.com", "provider2@example.com"]
    subject = "Quotation Approval Notification"
    body = "<p>Your quotation has been approved. Please find the attached documents.</p>"
    
    email_payload = [
        {
            "recipient_email": email,
            "subject": subject,
            "body": body,
            "priority": "high",
            "links": all_links,  # Use combined links including CDN URLs
        }
        for email in recipient_emails
    ]
    
    print(f"\nEmail payload for {len(recipient_emails)} recipients:")
    for i, payload in enumerate(email_payload, 1):
        print(f"  Recipient {i}: {payload['recipient_email']}")
        print(f"    Links: {len(payload['links'])} document links")
        for j, link in enumerate(payload['links'], 1):
            print(f"      {j}. {link}")
    
    # Verify results
    expected_count = len(test_documents)
    actual_count = len(document_cdn_links)
    
    print(f"\nExpected {expected_count} CDN links, got {actual_count}")
    
    if actual_count == expected_count:
        print("✅ Test PASSED: All documents processed successfully for approval email")
        return True
    else:
        print("❌ Test FAILED: Not all documents were processed")
        return False

if __name__ == "__main__":
    print("Quotation Approval Email Document Processing Test")
    print("="*55)
    
    # Run test
    test_passed = test_approval_email_document_processing()
    
    print("\n" + "="*55)
    print("Test Results:")
    print(f"Approval Email Document Processing: {'PASSED' if test_passed else 'FAILED'}")
    
    if test_passed:
        print("\n🎉 Test PASSED!")
        sys.exit(0)
    else:
        print("\n❌ Test FAILED!")
        sys.exit(1)
