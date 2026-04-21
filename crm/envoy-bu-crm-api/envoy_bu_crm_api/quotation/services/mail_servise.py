# app/services/gmail_oauth.py
from urllib.parse import urlencode
import requests
import json
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
import logging

from envoy_bu_crm_api.sales.models.core_models import GmailCredential

# Initialize logger
logger = logging.getLogger(__name__)

AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"
USERINFO_URI = "https://openidconnect.googleapis.com/v1/userinfo"
GMAIL_LIST_URI = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
GMAIL_THREAD_URI = "https://gmail.googleapis.com/gmail/v1/users/me/threads"
GMAIL_MESSAGE_URI = "https://gmail.googleapis.com/gmail/v1/users/me/messages"

def build_auth_url(state: str) -> str:
    """
    Build Google OAuth authorization URL with proper error handling.
    """
    try:
        if not settings.GOOGLE_CLIENT_ID:
            raise ValueError("GOOGLE_CLIENT_ID is not configured")
        if not settings.GOOGLE_REDIRECT_URI:
            raise ValueError("GOOGLE_REDIRECT_URI is not configured")
        if not settings.GOOGLE_SCOPES:
            raise ValueError("GOOGLE_SCOPES is not configured")
        
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": " ".join(settings.GOOGLE_SCOPES),
            "access_type": "offline",
            "prompt": "consent",
            "include_granted_scopes": "true",
            "state": state,
        }
        
        auth_url = f"{AUTH_URI}?{urlencode(params)}"
        logger.info(f"Built Google OAuth URL for state: {state}")
        return auth_url
        
    except Exception as e:
        logger.error(f"Error building auth URL: {str(e)}")
        raise

def exchange_code_for_tokens(code: str) -> dict:
    """
    Exchange authorization code for access tokens with proper error handling.
    """
    try:
        if not settings.GOOGLE_CLIENT_ID:
            raise ValueError("GOOGLE_CLIENT_ID is not configured")
        if not settings.GOOGLE_CLIENT_SECRET:
            raise ValueError("GOOGLE_CLIENT_SECRET is not configured")
        if not settings.GOOGLE_REDIRECT_URI:
            raise ValueError("GOOGLE_REDIRECT_URI is not configured")
        
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        
        logger.info("Exchanging authorization code for tokens")
        r = requests.post(TOKEN_URI, data=data, timeout=30)
        
        if r.status_code != 200:
            logger.error(f"Token exchange failed with status {r.status_code}: {r.text}")
            r.raise_for_status()
        
        token_response = r.json()
        
        if "access_token" not in token_response:
            logger.error(f"Token response missing access_token: {token_response}")
            raise ValueError("Google did not return access_token in response")
        
        logger.info("Successfully exchanged code for tokens")
        return token_response
        
    except requests.RequestException as e:
        logger.error(f"Request error during token exchange: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error during token exchange: {str(e)}")
        raise

def fetch_userinfo(access_token: str) -> dict:
    """
    Fetch user information from Google with proper error handling.
    """
    try:
        logger.info("Fetching user info from Google")
        r = requests.get(USERINFO_URI, headers={"Authorization": f"Bearer {access_token}"}, timeout=30)
        
        if r.status_code != 200:
            logger.error(f"Userinfo request failed with status {r.status_code}: {r.text}")
            r.raise_for_status()
        
        userinfo = r.json()
        
        if "email" not in userinfo:
            logger.error(f"Userinfo response missing email: {userinfo}")
            raise ValueError("Google userinfo response missing email field")
        
        logger.info(f"Successfully fetched user info for email: {userinfo.get('email')}")
        return userinfo
        
    except requests.RequestException as e:
        logger.error(f"Request error during userinfo fetch: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error during userinfo fetch: {str(e)}")
        raise

def upsert_credential(system_email: str, token_res: dict, user) -> GmailCredential:
    """
    Save or update Gmail credentials with proper error handling.
    """
    try:
        print("=== UPSERT_CREDENTIAL STARTED ===")
        print(f"System email: {system_email}")
        print(f"User: {user} (ID: {user.id})")
        print(f"Token response keys: {list(token_res.keys())}")
        
        access_token = token_res["access_token"]
        refresh_token = token_res.get("refresh_token")  # may be None on subsequent consents
        expires_in = int(token_res.get("expires_in", 3600))
        token_expiry = timezone.now() + timedelta(seconds=expires_in)

        print(f"Access token: {access_token[:20]}...")
        print(f"Refresh token: {refresh_token[:20] if refresh_token else 'None'}...")
        print(f"Expires in: {expires_in} seconds")
        print(f"Token expiry: {token_expiry}")

        logger.info(f"Upserting Gmail credentials for email: {system_email}, user_id: {user.id}")
        
        print("=== CREATING/UPDATING CREDENTIAL ===")
        print(f"Looking for existing credential with email: {system_email}")
        
        cred, created = GmailCredential.objects.get_or_create(
            system_email=system_email, 
            defaults={
                "user": user,
                "access_token": access_token,
                "refresh_token": refresh_token or "",
                "token_uri": TOKEN_URI,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "token_expiry": token_expiry,
            }
        )
        
        print(f"Credential {'created' if created else 'found existing'}")
        print(f"Credential ID: {cred.id}")
        
        # Update if existing
        print("=== UPDATING CREDENTIAL FIELDS ===")
        cred.user = user  # Update user even for existing records
        cred.access_token = access_token
        if refresh_token:  # keep old if google didn't return new one
            cred.refresh_token = refresh_token
        cred.client_id = settings.GOOGLE_CLIENT_ID
        cred.client_secret = settings.GOOGLE_CLIENT_SECRET
        cred.token_uri = TOKEN_URI
        cred.token_expiry = token_expiry
        
        print("=== SAVING CREDENTIAL TO DATABASE ===")
        cred.save()
        print("=== CREDENTIAL SAVED SUCCESSFULLY ===")
        
        action = "created" if created else "updated"
        logger.info(f"Gmail credentials {action} for email: {system_email}, user_id: {user.id}")
        return cred
        
    except Exception as e:
        print(f"=== UPSERT_CREDENTIAL ERROR ===")
        print(f"Error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        logger.error(f"Error upserting Gmail credentials for {system_email}, user_id: {user.id}: {str(e)}")
        raise

def is_expired(cred: GmailCredential) -> bool:
    """
    Check if Gmail credential token is expired.
    """
    try:
        is_exp = cred.token_expiry <= timezone.now() + timedelta(seconds=30)
        if is_exp:
            logger.info(f"Gmail token expired for email: {cred.system_email}")
        return is_exp
    except Exception as e:
        logger.error(f"Error checking token expiry for {cred.system_email}: {str(e)}")
        raise

def refresh_access_token(cred: GmailCredential) -> GmailCredential:
    """
    Refresh Gmail access token with proper error handling.
    """
    try:
        if not cred.refresh_token:
            raise RuntimeError("No refresh_token stored for this account.")
        
        logger.info(f"Refreshing access token for email: {cred.system_email}")
        
        data = {
            "client_id": cred.client_id,
            "client_secret": cred.client_secret,
            "refresh_token": cred.refresh_token,
            "grant_type": "refresh_token",
        }
        
        r = requests.post(cred.token_uri, data=data, timeout=30)
        
        if r.status_code != 200:
            logger.error(f"Token refresh failed with status {r.status_code}: {r.text}")
            r.raise_for_status()
        
        j = r.json()
        if "access_token" not in j:
            logger.error(f"Token refresh response missing access_token: {j}")
            raise RuntimeError(f"Google token refresh failed: {j}")
        
        cred.access_token = j["access_token"]
        expires_in = int(j.get("expires_in", 3600))
        cred.token_expiry = timezone.now() + timedelta(seconds=expires_in)
        cred.save()
        
        logger.info(f"Successfully refreshed access token for email: {cred.system_email}")
        return cred
        
    except requests.RequestException as e:
        logger.error(f"Request error during token refresh for {cred.system_email}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error refreshing access token for {cred.system_email}: {str(e)}")
        raise

def ensure_fresh_token(cred: GmailCredential) -> GmailCredential:
    """
    Ensure Gmail credential has a fresh token.
    """
    try:
        if is_expired(cred):
            return refresh_access_token(cred)
        return cred
    except Exception as e:
        logger.error(f"Error ensuring fresh token for {cred.system_email}: {str(e)}")
        raise

def list_messages(cred: GmailCredential, q: str = "", label="INBOX", max_results=10) -> dict:
    """
    List Gmail messages with proper error handling.
    """
    try:
        cred = ensure_fresh_token(cred)
        
        logger.info(f"Listing Gmail messages for {cred.system_email}, label: {label}, max: {max_results}")
        
        params = {"labelIds": label, "maxResults": max_results}
        if q:
            params["q"] = q
        
        r = requests.get(
            GMAIL_LIST_URI,
            headers={"Authorization": f"Bearer {cred.access_token}"},
            params=params,
            timeout=30,
        )
        
        if r.status_code != 200:
            logger.error(f"Gmail messages request failed with status {r.status_code}: {r.text}")
            r.raise_for_status()
        
        data = r.json()
        message_count = len(data.get('messages', []))
        logger.info(f"Successfully retrieved {message_count} messages for {cred.system_email}")
        
        return data
        
    except requests.RequestException as e:
        logger.error(f"Request error listing Gmail messages for {cred.system_email}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error listing Gmail messages for {cred.system_email}: {str(e)}")
        raise

def _add_attachments_to_message(message, attachments):
    """
    Add attachments to a MIME message
    
    Args:
        message: MIMEMultipart message object
        attachments: List of attachment objects with 'filename', 'content_type', and 'data' keys
    
    Returns:
        None (modifies message in place)
    """
    if attachments and isinstance(attachments, list):
        for attachment in attachments:
            try:
                if isinstance(attachment, dict) and 'filename' in attachment and 'data' in attachment:
                    filename = attachment.get('filename', 'attachment')
                    content_type = attachment.get('content_type', 'application/octet-stream')
                    data = attachment.get('data')
                    
                    # Create attachment part with proper MIME type
                    if content_type.startswith('text/'):
                        attachment_part = MIMEText(data.decode('utf-8'), content_type.split('/')[1])
                    elif content_type.startswith('image/'):
                        attachment_part = MIMEImage(data)
                    else:
                        # For other types, use MIMEBase with proper content type
                        main_type, sub_type = content_type.split('/', 1) if '/' in content_type else ('application', 'octet-stream')
                        attachment_part = MIMEBase(main_type, sub_type)
                        attachment_part.set_payload(data)
                    
                    # Add headers
                    attachment_part.add_header('Content-Disposition', 'attachment', filename=filename)
                    
                    # Encode the attachment
                    from email import encoders
                    encoders.encode_base64(attachment_part)
                    
                    message.attach(attachment_part)
                    logger.info(f"Successfully attached file: {filename} ({content_type})")
            except Exception as e:
                logger.warning(f"Failed to attach file {attachment.get('filename', 'unknown')}: {e}")
                continue


def send_email(credential, to_email, subject, body, thread_id=None, reply_to_message_id=None, attachments=None):
    """
    Send email via Gmail API
    
    Args:
        credential: GmailCredential object
        to_email: Recipient email address
        subject: Email subject
        body: Email body (HTML or plain text)
        thread_id: Gmail thread ID for replies (optional)
        reply_to_message_id: Gmail message ID to reply to (optional)
        attachments: List of attachment objects with 'filename', 'content_type', and 'data' keys (optional)
    
    Returns:
        dict: Response from Gmail API with message ID and thread ID
    """
    try:
        credential = ensure_fresh_token(credential)
        
        # Create email message - use 'mixed' if there are attachments, 'alternative' otherwise
        if attachments:
            message = MIMEMultipart('mixed')
        else:
            message = MIMEMultipart('alternative')
            
        message['to'] = to_email
        message['from'] = credential.system_email
        message['subject'] = subject
        
        # Add proper threading headers for replies
        if thread_id and reply_to_message_id:
            # Get the original message details to extract proper headers
            try:
                original_message = get_message_details(credential, reply_to_message_id)
                if original_message:
                    # Extract Message-ID from original message
                    headers = original_message.get('payload', {}).get('headers', [])
                    original_message_id = None
                    original_references = None
                    
                    for header in headers:
                        if header['name'].lower() == 'message-id':
                            original_message_id = header['value']
                        elif header['name'].lower() == 'references':
                            original_references = header['value']
                    
                    # Set In-Reply-To header
                    if original_message_id:
                        message['In-Reply-To'] = original_message_id
                        logger.info(f"Set In-Reply-To header: {original_message_id}")
                    
                    # Set References header (chain of message IDs)
                    if original_references:
                        message['References'] = f"{original_references} {original_message_id}"
                    elif original_message_id:
                        message['References'] = original_message_id
                    
                    logger.info(f"Set threading headers for reply to message {reply_to_message_id}")
                    
            except Exception as e:
                logger.warning(f"Could not set threading headers: {e}")
                # Continue without threading headers if we can't get them
        
        # Add body
        if attachments:
            # When there are attachments, create a nested alternative part for the body
            body_part = MIMEMultipart('alternative')
            text_part = MIMEText(body, 'plain')
            html_part = MIMEText(body, 'html')
            body_part.attach(text_part)
            body_part.attach(html_part)
            message.attach(body_part)
        else:
            # No attachments, attach body parts directly
            text_part = MIMEText(body, 'plain')
            html_part = MIMEText(body, 'html')
            message.attach(text_part)
            message.attach(html_part)
        
        # Add attachments if provided
        _add_attachments_to_message(message, attachments)
        
        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Prepare API request
        gmail_api_url = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
        headers = {
            "Authorization": f"Bearer {credential.access_token}",
            "Content-Type": "application/json"
        }
        
        # Prepare request body
        request_body = {
            "raw": raw_message
        }
        
        # If this is a reply, add thread ID
        if thread_id:
            request_body["threadId"] = thread_id
        
        # Send the email
        r = requests.post(gmail_api_url, headers=headers, json=request_body)
        r.raise_for_status()
        
        response_data = r.json()
        logger.info(f"Email sent successfully. Message ID: {response_data.get('id')}, Thread ID: {response_data.get('threadId')}")
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise

def create_draft(credential, to_email, subject, body, thread_id=None):
    """
    Create a draft email via Gmail API
    
    Args:
        credential: GmailCredential object
        to_email: Recipient email address
        subject: Email subject
        body: Email body
        thread_id: Gmail thread ID for replies (optional)
    
    Returns:
        dict: Response from Gmail API with draft ID
    """
    try:
        credential = ensure_fresh_token(credential)
        
        # Create email message
        message = MIMEMultipart('alternative')
        message['to'] = to_email
        message['from'] = credential.system_email
        message['subject'] = subject
        
        # Add body
        text_part = MIMEText(body, 'plain')
        html_part = MIMEText(body, 'html')
        message.attach(text_part)
        message.attach(html_part)
        
        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Prepare API request
        gmail_api_url = "https://gmail.googleapis.com/gmail/v1/users/me/drafts"
        headers = {
            "Authorization": f"Bearer {credential.access_token}",
            "Content-Type": "application/json"
        }
        
        # Prepare request body
        request_body = {
            "message": {
                "raw": raw_message
            }
        }
        
        # If this is a reply, add thread ID
        if thread_id:
            request_body["message"]["threadId"] = thread_id
        
        # Create the draft
        r = requests.post(gmail_api_url, headers=headers, json=request_body)
        r.raise_for_status()
        
        response_data = r.json()
        logger.info(f"Draft created successfully. Draft ID: {response_data.get('id')}")
        
        return response_data
        
    except Exception as e:
        logger.error(f"Error creating draft: {str(e)}")
        raise

def get_thread_messages(cred: GmailCredential, thread_id: str) -> dict:
    """
    Get all messages from a specific Gmail thread.
    
    Args:
        cred: GmailCredential object
        thread_id: Gmail thread ID
    
    Returns:
        dict: Thread data with messages
    """
    try:
        cred = ensure_fresh_token(cred)
        
        logger.info(f"Fetching thread messages for thread ID: {thread_id}")
        
        url = f"{GMAIL_THREAD_URI}/{thread_id}"
        headers = {
            "Authorization": f"Bearer {cred.access_token}",
            "Content-Type": "application/json"
        }
        
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        
        thread_data = r.json()
        message_count = len(thread_data.get('messages', []))
        logger.info(f"Successfully retrieved {message_count} messages from thread {thread_id}")
        
        return thread_data
        
    except requests.RequestException as e:
        logger.error(f"Request error fetching thread messages for thread {thread_id}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error fetching thread messages for thread {thread_id}: {str(e)}")
        raise

def get_message_details(cred: GmailCredential, message_id: str) -> dict:
    """
    Get detailed information about a specific Gmail message.
    
    Args:
        cred: GmailCredential object
        message_id: Gmail message ID
    
    Returns:
        dict: Message details
    """
    try:
        cred = ensure_fresh_token(cred)
        
        logger.info(f"Fetching message details for message ID: {message_id}")
        
        url = f"{GMAIL_MESSAGE_URI}/{message_id}"
        headers = {
            "Authorization": f"Bearer {cred.access_token}",
            "Content-Type": "application/json"
        }
        
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        
        message_data = r.json()
        logger.info(f"Successfully retrieved message details for message {message_id}")
        
        return message_data
        
    except requests.RequestException as e:
        logger.error(f"Request error fetching message details for message {message_id}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error fetching message details for message {message_id}: {str(e)}")
        raise


def get_attachment(cred: GmailCredential, message_id: str, attachment_id: str) -> dict:
    """
    Get attachment data from Gmail.
    
    Args:
        cred: GmailCredential object
        message_id: Gmail message ID
        attachment_id: Gmail attachment ID
    
    Returns:
        dict: Attachment data with 'data' field containing base64 encoded file content
    """
    try:
        cred = ensure_fresh_token(cred)
        
        logger.info(f"Fetching attachment {attachment_id} from message {message_id}")
        
        url = f"{GMAIL_MESSAGE_URI}/{message_id}/attachments/{attachment_id}"
        headers = {
            "Authorization": f"Bearer {cred.access_token}",
            "Content-Type": "application/json"
        }
        
        r = requests.get(url, headers=headers, timeout=60)  # Longer timeout for file downloads
        r.raise_for_status()
        
        attachment_data = r.json()
        logger.info(f"Successfully retrieved attachment {attachment_id} from message {message_id}")
        
        return attachment_data
        
    except requests.RequestException as e:
        logger.error(f"Request error fetching attachment {attachment_id} from message {message_id}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error fetching attachment {attachment_id} from message {message_id}: {str(e)}")
        raise

def search_messages_by_conversation(cred: GmailCredential, conversation_code: str, max_results: int = 50) -> dict:
    """
    Search for messages that might be part of a conversation using various search criteria.
    
    Args:
        cred: GmailCredential object
        conversation_code: Conversation code to search for
        max_results: Maximum number of results to return
    
    Returns:
        dict: Search results
    """
    try:
        cred = ensure_fresh_token(cred)
        
        logger.info(f"Searching for messages with conversation code: {conversation_code}")
        
        # Try different search queries to find related messages
        search_queries = [
            f"subject:{conversation_code}",
            f"body:{conversation_code}",
            f"from:{conversation_code}",
            f"to:{conversation_code}"
        ]
        
        all_messages = []
        
        for query in search_queries:
            try:
                params = {
                    "q": query,
                    "maxResults": max_results
                }
                
                r = requests.get(
                    GMAIL_LIST_URI,
                    headers={"Authorization": f"Bearer {cred.access_token}"},
                    params=params,
                    timeout=30
                )
                r.raise_for_status()
                
                data = r.json()
                messages = data.get('messages', [])
                all_messages.extend(messages)
                
                logger.info(f"Found {len(messages)} messages for query: {query}")
                
            except Exception as e:
                logger.warning(f"Error searching with query '{query}': {str(e)}")
                continue
        
        # Remove duplicates based on message ID
        unique_messages = []
        seen_ids = set()
        for msg in all_messages:
            if msg['id'] not in seen_ids:
                unique_messages.append(msg)
                seen_ids.add(msg['id'])
        
        logger.info(f"Total unique messages found: {len(unique_messages)}")
        
        return {
            "messages": unique_messages[:max_results],
            "total_found": len(unique_messages)
        }
        
    except requests.RequestException as e:
        logger.error(f"Request error searching messages for conversation {conversation_code}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error searching messages for conversation {conversation_code}: {str(e)}")
        raise

