#!/usr/bin/env python3
"""
Reset Gmail credentials to force re-authentication with new scopes
"""

import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'envoy.settings')

# Setup Django
django.setup()

# Now we can import Django models
from envoy.models.mail_model import GmailCredential

print("Reset Gmail Credentials")
print("="*50)

# Get current credentials
credentials = GmailCredential.objects.all()
print(f"Found {credentials.count()} Gmail credentials in database:")

for cred in credentials:
    print(f"  - {cred.system_email} (expires: {cred.token_expiry})")

if credentials.count() > 0:
    print(f"\nThese credentials were obtained with old scopes that don't include send permissions.")
    print(f"To fix the 403 Forbidden error, we need to delete them so users can re-authenticate.")
    
    response = input(f"\nDo you want to delete all {credentials.count()} Gmail credentials? (y/N): ")
    
    if response.lower() == 'y':
        # Delete all credentials
        deleted_count = credentials.count()
        credentials.delete()
        print(f"✅ Deleted {deleted_count} Gmail credentials.")
        
        print(f"\nNext steps:")
        print(f"1. Restart your Django server")
        print(f"2. Users need to re-authenticate with Google:")
        print(f"   - Visit: http://127.0.0.1:8000/api/auth-google-start")
        print(f"   - Complete the OAuth flow again")
        print(f"3. The new tokens will have the correct send permissions")
        
    else:
        print(f"❌ Operation cancelled. Credentials were not deleted.")
        print(f"\nTo manually delete credentials, you can:")
        print(f"1. Use Django admin interface")
        print(f"2. Or run this command in Django shell:")
        print(f"   python manage.py shell")
        print(f"   >>> from envoy.models.mail_model import GmailCredential")
        print(f"   >>> GmailCredential.objects.all().delete()")
else:
    print(f"✅ No Gmail credentials found in database.")
    print(f"Users can authenticate with Google using the correct scopes.")

print(f"\n" + "="*50)
print("Summary:")
print("The 403 Forbidden error occurs because existing tokens")
print("don't have the new send permissions. After deleting credentials")
print("and re-authenticating, the email sending will work correctly.")
