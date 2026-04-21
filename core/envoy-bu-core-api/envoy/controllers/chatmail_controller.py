import logging
import os
from django.db import models
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from envoy.models.chat_conversation import ChatConversation
from envoy.models.email_message import EmailChatMessage
from envoy.models.email_attachment import EmailAttachment
from envoy.models.mail_model import GmailCredential
from envoy.services import email_service as svc
from envoy.services.email_service import ensure_fresh_token
from mServices.QueryBuilderService import QueryBuilderService
from mServices.ResponseService import ResponseService

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def send_chatmail_message(request):
    """
    Send a chatmail message and store it in our database tables.
    If conversation_id is provided, it will be sent as a reply in the same conversation.
    """
    try:
        # Extract data from request
        to_email = request.data.get('to_email')
        from_email = request.data.get('from_email')
        subject = request.data.get('subject')
        body = request.data.get('body')
        conversation_id = request.data.get('conversation_id')
        attachments = request.data.get('attachments', [])
        documents = request.data.get('documents', [])
        
        # Process documents if provided (for backward compatibility)
        if documents and not attachments:
            import os
            for doc in documents:
                if isinstance(doc, dict) and doc.get("doc"):
                    # Use the S3 URL directly instead of base64 data
                    doc_key = doc.get("doc", "")
                    cdn_base_url = os.getenv("CDN_BASE_URL")
                    doc_url = f"{cdn_base_url}/{doc_key}"
                    doc_name = doc.get("name", "document.pdf")
                    
                    # Use provided type from payload, fallback to file extension detection
                    provided_type = doc.get("type", "")
                    if provided_type:
                        content_type = provided_type
                    else:
                        # Determine content type based on file extension
                        if doc_name.lower().endswith('.xlsx'):
                            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        elif doc_name.lower().endswith('.pdf'):
                            content_type = "application/pdf"
                        elif doc_name.lower().endswith('.docx'):
                            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        else:
                            content_type = "application/octet-stream"
                    
                    # Use provided size from payload, fallback to 0
                    provided_size = doc.get("size", "")
                    try:
                        size_bytes = int(provided_size) if provided_size else 0
                    except (ValueError, TypeError):
                        size_bytes = 0
                    
                    attachment = {
                        "filename": doc_name,
                        "content_type": content_type,
                        "file_url": doc_url,  # Use S3 URL instead of base64 data
                        "size_bytes": size_bytes
                    }
                    attachments.append(attachment)
                    logger.info(f"[send_chatmail_message] Added attachment: {attachment['filename']} with URL: {doc_url}, size: {size_bytes} bytes, type: {content_type}")
        
        # Get user from request
        user = request.user
        
        # Normalize email formats to ensure consistency
        def normalize_email_format(email_string):
            """Normalize email format to extract just the email address"""
            if not email_string:
                return ""
            
            email_string = email_string.strip()
            
            # Handle "Name <email@domain.com>" format
            if "<" in email_string and ">" in email_string:
                start = email_string.find("<") + 1
                end = email_string.find(">")
                if start < end:
                    return email_string[start:end].strip().lower()
            
            # Handle raw email format
            return email_string.lower()
        
        # If conversation_id is provided, try to derive addresses when missing
        if conversation_id:
            try:
                logger.info(f"[DEBUG] Looking for conversation_id: {conversation_id}")
                
                # Get the conversation
                conversation = ChatConversation.objects.get(id=conversation_id)
                
                # Derive to_email from conversation's insurer_id if not provided
                if not to_email and conversation.insurer_id:
                    try:
                        insurer_record = (
                            QueryBuilderService("core_service_providers")
                            .select("email")
                            .where("id", conversation.insurer_id)
                            .first()
                        )
                        if insurer_record and insurer_record.get("email"):
                            to_email = insurer_record["email"].strip()
                            logger.info(f"[send_chatmail_message] Derived to_email '{to_email}' from conversation insurer_id {conversation.insurer_id}")
                        else:
                            logger.warning(f"[send_chatmail_message] No email found for insurer_id {conversation.insurer_id}")
                    except Exception as e:
                        logger.error(f"[send_chatmail_message] Error deriving to_email from conversation insurer_id {conversation.insurer_id}: {e}")
                
                # If still no to_email, try to derive from latest email in conversation (fallback)
                if not to_email:
                    latest_email = (
                        EmailChatMessage.objects
                        .filter(conversation_id=conversation_id)
                        .order_by("-sent_at", "-id")
                        .first()
                    )
                    if latest_email:
                        logger.info(f"[DEBUG] Found latest email: from='{latest_email.from_email}', to='{latest_email.to_email}'")
                        to_email = latest_email.to_email
                        logger.info(f"[send_chatmail_message] Derived to_email '{to_email}' from latest email in conversation_id {conversation_id}")
                    else:
                        logger.warning(f"[send_chatmail_message] No EmailChatMessage found for conversation_id {conversation_id}")
                
                # For from_email, we ALWAYS prefer the default system email from Gmail credentials
                # Only use latest email's from_email if no system email is available
                if not from_email:
                    # Try to get default system email from Gmail credentials first
                    try:
                        gmail_credential_row = (
                            QueryBuilderService("core_gmailcredential")
                            .select("system_email")
                            .orderBy("id", "asc")
                            .first()
                        )
                        if gmail_credential_row and gmail_credential_row.get("system_email"):
                            from_email = gmail_credential_row["system_email"]
                            logger.info(f"[send_chatmail_message] Using default from_email from Gmail credentials: {from_email}")
                        else:
                            # Fallback to latest email's from_email only if no system email found
                            latest_email = (
                                EmailChatMessage.objects
                                .filter(conversation_id=conversation_id)
                                .order_by("-sent_at", "-id")
                                .first()
                            )
                            if latest_email:
                                from_email = latest_email.from_email
                                logger.info(f"[send_chatmail_message] Fallback: Derived from_email '{from_email}' from latest email in conversation_id {conversation_id}")
                            else:
                                logger.warning(f"[send_chatmail_message] No system email found and no EmailChatMessage for conversation_id {conversation_id}")
                    except Exception as e:
                        logger.error(f"[send_chatmail_message] Error getting default system email: {e}")
                        
            except ChatConversation.DoesNotExist:
                logger.error(f"[send_chatmail_message] Conversation with ID {conversation_id} not found")
            except Exception as e:
                logger.error(f"[send_chatmail_message] Error deriving emails for conversation_id={conversation_id}: {e}")
        
        # If no conversation_id provided, try to derive from_email from Gmail credentials
        if not conversation_id and not from_email:
            try:
                gmail_credential_row = (
                    QueryBuilderService("core_gmailcredential")
                    .select("system_email")
                    .orderBy("id", "asc")
                    .first()
                )
                if gmail_credential_row and gmail_credential_row.get("system_email"):
                    from_email = gmail_credential_row["system_email"]
                    logger.info(f"[send_chatmail_message] Using default from_email from Gmail credentials: {from_email}")
                else:
                    logger.warning(f"[send_chatmail_message] No default system_email found in core_gmailcredential")
            except Exception as e:
                logger.warning(f"[send_chatmail_message] Could not load default system_email: {e}")
        
        # If creating new conversation and to_email is missing, try to derive from insurer_id
        if not conversation_id and not to_email:
            insurer_id = request.data.get('insurer_id')
            if insurer_id:
                try:
                    insurer_record = (
                        QueryBuilderService("core_service_providers")
                        .select("email")
                        .where("id", insurer_id)
                        .first()
                    )
                    if insurer_record and insurer_record.get("email"):
                        to_email = insurer_record["email"].strip()
                        logger.info(f"[send_chatmail_message] Derived to_email '{to_email}' from insurer_id {insurer_id}")
                    else:
                        logger.warning(f"[send_chatmail_message] No email found for insurer_id {insurer_id}")
                except Exception as e:
                    logger.error(f"[send_chatmail_message] Error deriving to_email from insurer_id {insurer_id}: {e}")
        
        # Normalize email formats
        to_email = normalize_email_format(to_email)
        from_email = normalize_email_format(from_email)
        
        # Debug logging after normalization
        logger.info(f"[DEBUG] After normalization:")
        logger.info(f"[DEBUG] to_email: '{to_email}'")
        logger.info(f"[DEBUG] from_email: '{from_email}'")
        
        # Validate required fields based on whether conversation_id is provided
        if conversation_id:
            # For existing conversations, only body is required
            if not body:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {"body": ["body is required when replying to existing conversation"]},
                    "Validation error"
                )
            
            # Subject is optional for replies (can use "Re: " + original subject)
            if not subject:
                # Try to get subject from the latest message in the conversation
                try:
                    latest_message = (
                        EmailChatMessage.objects
                        .filter(conversation_id=conversation_id)
                        .order_by("-sent_at", "-id")
                        .first()
                    )
                    if latest_message and latest_message.subject:
                        # Remove existing "Re: " prefix if present to avoid "Re: Re: ..."
                        original_subject = latest_message.subject
                        if original_subject.lower().startswith('re: '):
                            original_subject = original_subject[4:].strip()
                        subject = f"Re: {original_subject}"
                        logger.info(f"[send_chatmail_message] Auto-generated subject: {subject}")
                    else:
                        subject = "Re: Message"
                        logger.info(f"[send_chatmail_message] Using default subject: {subject}")
                except Exception as e:
                    subject = "Re: Message"
                    logger.warning(f"[send_chatmail_message] Error getting subject from conversation: {e}")
            else:
                # Ensure subject starts with "Re: " for proper threading
                if not subject.lower().startswith('re: '):
                    subject = f"Re: {subject}"
                    logger.info(f"[send_chatmail_message] Added 'Re: ' prefix to subject: {subject}")
        else:
            # For new conversations, all fields are required
            if not to_email:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {"to_email": ["to_email is required for new conversations"]},
                    "Validation error"
                )
            
            if not subject:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {"subject": ["subject is required for new conversations"]},
                    "Validation error"
                )
            
            if not body:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {"body": ["body is required for new conversations"]},
                    "Validation error"
                )
            
            if not from_email:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {"from_email": ["from_email is required for new conversations"]},
                    "Validation error"
                )
        
        # Check if Gmail is connected for the sender email
        try:
            cred = GmailCredential.objects.get(system_email=from_email)
            # Ensure token is fresh before using it
            cred = ensure_fresh_token(cred)
        except GmailCredential.DoesNotExist:
            return ResponseService.response(
                "UNAUTHORIZED",
                {
                    "connected": False,
                    "action": "connect_first",
                    "email": from_email
                },
                f"Gmail account {from_email} is not connected. Please connect your Gmail account first."
            )
        
        # Handle conversation (existing or new)
        if conversation_id:
            # Reply to existing conversation
            try:
                conversation = ChatConversation.objects.get(id=conversation_id)
                logger.info(f"Replying to existing conversation: {conversation.code}")
            except ChatConversation.DoesNotExist:
                return ResponseService.response(
                    "NOT_FOUND",
                    None,
                    f"Conversation with ID {conversation_id} not found"
                )
        else:
            # Create new conversation
            conversation_type = request.data.get('conversation_type', 'QUOTATION')
            type_based_id = request.data.get('type_based_id')
            insurer_id = request.data.get('insurer_id')
            
            conversation = ChatConversation.objects.create(
                type=conversation_type,
                type_based_id=type_based_id,
                insurer_id=insurer_id,
                user=user,
                gmail_thread_id=None  # Will be set after first email is sent
            )
            logger.info(f"Created new conversation: {conversation.code}")

        # Create email message record (outgoing message is seen by the sender)
        email_message = EmailChatMessage.objects.create(
            conversation=conversation,
            gmail_message_id=None,  # Will be set after Gmail API call
            gmail_thread_id=conversation.gmail_thread_id,
            from_email=from_email,
            to_email=to_email,
            subject=subject,
            body=body,
            sent_at=None,  # Will be set after successful send
            is_seen=True,
        )

        # Handle attachments - convert base64 data back to bytes for email service
        email_attachments = []
        for attachment_data in attachments:
            # Create database record
            EmailAttachment.objects.create(
                email_message=email_message,
                file_name=attachment_data.get('filename') or attachment_data.get('file_name'),
                file_url=attachment_data.get('file_url'),
                content_type=attachment_data.get('content_type'),
                size_bytes=attachment_data.get('size_bytes', 0),
                gmail_attachment_id=attachment_data.get('gmail_attachment_id'),
                is_image=attachment_data.get('is_image', False)
            )
            
            # Prepare attachment for email service
            if attachment_data.get('data'):
                import base64
                try:
                    # Convert base64 string back to bytes
                    if isinstance(attachment_data['data'], str):
                        attachment_bytes = base64.b64decode(attachment_data['data'])
                    else:
                        attachment_bytes = attachment_data['data']
                    
                    email_attachment = {
                        'filename': attachment_data.get('filename') or attachment_data.get('file_name', 'attachment'),
                        'content_type': attachment_data.get('content_type', 'application/octet-stream'),
                        'data': attachment_bytes
                    }
                    email_attachments.append(email_attachment)
                    logger.info(f"[send_chatmail_message] Prepared attachment: {email_attachment['filename']}")
                except Exception as e:
                    logger.error(f"[send_chatmail_message] Error processing attachment: {e}")
                    continue
            elif attachment_data.get('file_url'):
                # Handle S3 URL attachments - download the file and attach it
                try:
                    import requests
                    file_url = attachment_data.get('file_url')
                    filename = attachment_data.get('filename') or attachment_data.get('file_name', 'attachment')
                    content_type = attachment_data.get('content_type', 'application/octet-stream')
                    
                    # Download the file from S3 URL
                    response = requests.get(file_url, timeout=30)
                    response.raise_for_status()
                    
                    email_attachment = {
                        'filename': filename,
                        'content_type': content_type,
                        'data': response.content
                    }
                    email_attachments.append(email_attachment)
                    logger.info(f"[send_chatmail_message] Downloaded and prepared S3 attachment: {filename} from {file_url}")
                except Exception as e:
                    logger.error(f"[send_chatmail_message] Error downloading S3 attachment from {attachment_data.get('file_url')}: {e}")
                    continue

        # Send email via Gmail API
        try:
            logger.info(f"[DEBUG] Final email details:")
            logger.info(f"[DEBUG] from_email: '{from_email}'")
            logger.info(f"[DEBUG] to_email: '{to_email}'")
            logger.info(f"[DEBUG] subject: '{subject}'")
            logger.info(f"[DEBUG] body length: {len(body) if body else 0}")
            logger.info(f"[DEBUG] thread_id: '{conversation.gmail_thread_id}'")
            
            # Validate email addresses before sending
            if not from_email or not to_email:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {
                        "from_email": from_email,
                        "to_email": to_email
                    },
                    f"Invalid email addresses: from_email='{from_email}', to_email='{to_email}'"
                )
            
            # Get the latest message ID for proper threading
            reply_to_message_id = None
            if conversation_id and conversation.gmail_thread_id:
                try:
                    latest_message = (
                        EmailChatMessage.objects
                        .filter(conversation_id=conversation_id)
                        .exclude(gmail_message_id__isnull=True)
                        .exclude(gmail_message_id='')
                        .order_by("-sent_at", "-id")
                        .first()
                    )
                    if latest_message and latest_message.gmail_message_id:
                        reply_to_message_id = latest_message.gmail_message_id
                        logger.info(f"[send_chatmail_message] Using reply_to_message_id: {reply_to_message_id}")
                except Exception as e:
                    logger.warning(f"[send_chatmail_message] Could not get latest message ID for threading: {e}")
            
            logger.info(f"Sending email from {from_email} to {to_email}")
            logger.info(f"[send_chatmail_message] Sending with {len(email_attachments)} attachments")
            gmail_response = svc.send_email(
                credential=cred,
                to_email=to_email,
                subject=subject,
                body=body,
                thread_id=conversation.gmail_thread_id,
                reply_to_message_id=reply_to_message_id,
                attachments=email_attachments
            )
            
            # Update message with Gmail details
            email_message.gmail_message_id = gmail_response.get('id')
            email_message.sent_at = timezone.now()
            email_message.save()

            # Update conversation with Gmail thread ID if it's the first message
            if not conversation.gmail_thread_id:
                conversation.gmail_thread_id = gmail_response.get('threadId')
                conversation.save()

            logger.info(f"Email sent successfully: {email_message.id}")
            
            return ResponseService.response(
                "SUCCESS",
                {
                    'message_id': email_message.id,
                    'conversation_id': conversation.id,
                    'conversation_code': conversation.code,
                    'gmail_thread_id': conversation.gmail_thread_id,
                    'gmail_message_id': email_message.gmail_message_id
                },
                "Email sent successfully"
            )
            
        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            return ResponseService.response(
                "INTERNAL_SERVER_ERROR",
                None,
                f"Failed to send email: {str(e)}"
            )

    except Exception as e:
        logger.error(f"Error in send_chatmail_message: {str(e)}")
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            None,
            f"Internal server error: {str(e)}"
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chatmail_messages(request):
    """Get chatmail messages with optional Gmail sync"""
    try:
        conversation_id = request.GET.get('conversation_id')
        user_id = request.GET.get('user_id')
        sync_thread = request.GET.get('sync_thread', 'false').lower() == 'true'
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        if not conversation_id:
            return Response(
                {
                    "error": "Missing required field",
                    "message": "conversation_id is required",
                    "error_code": "MISSING_CONVERSATION_ID"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Sync with Gmail if requested
        sync_info = None
        if sync_thread:
            sync_result = sync_gmail_thread_messages(conversation_id)
            if not sync_result['success']:
                return Response(
                    {
                        "error": "Thread sync failed",
                        "message": sync_result['message'],
                        "error_code": "THREAD_SYNC_FAILED"
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            sync_info = sync_result['data']
        
        messages = EmailChatMessage.objects.all()
        messages = messages.filter(conversation_id=conversation_id)
        
        if user_id:
            messages = messages.filter(conversation__user_id=user_id)
        
        # Optimize queries with proper select_related and prefetch_related
        messages = messages.select_related('conversation').prefetch_related('attachments')
        messages = messages.order_by('-sent_at', '-id')
        
        # Get total count efficiently
        total_count = messages.count()
        
        # Paginate results
        start = (page - 1) * page_size
        end = start + page_size
        paginated_messages = messages[start:end]
        
        # Build response data efficiently
        message_data = []
        for message in paginated_messages:
            # Use prefetched attachments to avoid N+1 queries
            attachments_data = []
            for att in message.attachments.all():
                attachment_data = {
                    'id': att.id,
                    'file_name': att.file_name,
                    'content_type': att.content_type,
                    'size_bytes': att.size_bytes,
                    'is_image': att.is_image
                }
                
                # Keep the original gmail:// format for file_url
                attachment_data['file_url'] = att.file_url
                
                # Add clickable URLs for direct access
                if att.file and att.file.name:
                    # File is stored locally - use direct media URL
                    base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
                    direct_url = f"{base_url}{att.file.url}"
                    attachment_data['download_url'] = direct_url
                    attachment_data['view_url'] = direct_url if att.is_image else None
                else:
                    # Fallback to download endpoint if file not stored locally
                    base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
                    download_url = f"{base_url}/api/chatmail/download-attachment?attachment_id={att.id}"
                    attachment_data['download_url'] = download_url
                    attachment_data['view_url'] = download_url if att.is_image else None
                
                attachments_data.append(attachment_data)
            
            message_data.append({
                'id': message.id,
                'conversation_id': message.conversation_id,
                'conversation_code': message.conversation.code,
                'from_email': message.from_email,
                'to_email': message.to_email,
                'subject': message.subject,
                'body': message.body,
                'sent_at': message.sent_at,
                'gmail_message_id': message.gmail_message_id,
                'is_seen': getattr(message, 'is_seen', False),
                'attachments': attachments_data
            })
        
        response_data = {
            'messages': message_data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        }
        
        # Add sync info if Gmail sync was performed
        if sync_info:
            response_data['sync_info'] = sync_info
            message = "Messages retrieved successfully with Gmail sync"
        else:
            message = "Messages retrieved successfully from database"
        
        return Response(
            {
                "success": True,
                "message": message,
                "data": response_data
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error in get_chatmail_messages: {str(e)}")
        return Response(
            {
                "error": "Internal server error",
                "message": f"Internal server error: {str(e)}",
                "error_code": "INTERNAL_SERVER_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_gmail_thread(request):
    """
    Sync Gmail thread messages for a specific conversation.
    This endpoint fetches all messages from the Gmail thread and stores them in our database.
    """
    try:
        conversation_id = request.data.get('conversation_id')
        
        if not conversation_id:
            return Response(
                {
                    "error": "Missing required field",
                    "message": "conversation_id is required",
                    "error_code": "MISSING_CONVERSATION_ID"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Sync the thread
        sync_result = sync_gmail_thread_messages(conversation_id)
        
        if sync_result['success']:
            return Response(
                {
                    "success": True,
                    "message": "Gmail thread synced successfully",
                    "data": sync_result['data']
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "error": "Thread sync failed",
                    "message": sync_result['message'],
                    "error_code": "THREAD_SYNC_FAILED"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Error in sync_gmail_thread: {str(e)}")
        return Response(
            {
                "error": "Internal server error",
                "message": f"Internal server error: {str(e)}",
                "error_code": "INTERNAL_SERVER_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )





def sync_gmail_thread_messages(conversation_id):
    """
    Optimized helper function to sync Gmail thread messages for a conversation.
    Returns a dict with success status and data/error message.
    """
    try:
        # Get the conversation
        try:
            conversation = ChatConversation.objects.get(id=conversation_id)
        except ChatConversation.DoesNotExist:
            return {
                'success': False,
                'message': f"Conversation with ID {conversation_id} not found"
            }
        
        # Check if conversation has a Gmail thread ID
        if not conversation.gmail_thread_id:
            return {
                'success': False,
                'message': f"Conversation {conversation_id} does not have a Gmail thread ID"
            }
        
        # Get any Gmail credential (we'll use the first one for now)
        try:
            cred = GmailCredential.objects.first()
            if not cred:
                return {
                    'success': False,
                    'message': "No Gmail credentials found. Please connect a Gmail account first."
                }
            # Ensure token is fresh before using it
            cred = ensure_fresh_token(cred)
        except GmailCredential.DoesNotExist:
            return {
                'success': False,
                'message': "No Gmail credentials found. Please connect a Gmail account first."
            }
        
        # Get all existing message IDs for this conversation to avoid processing duplicates
        existing_message_ids = set(
            EmailChatMessage.objects.filter(
                conversation=conversation
            ).values_list('gmail_message_id', flat=True)
        )
        
        # Also get messages with empty bodies that need to be updated
        messages_with_empty_bodies = EmailChatMessage.objects.filter(
            conversation=conversation,
            body__isnull=True
        ) | EmailChatMessage.objects.filter(
            conversation=conversation,
            body=''
        )
        
        # Create a set of message IDs that need body updates
        messages_needing_body_update = set(
            messages_with_empty_bodies.values_list('gmail_message_id', flat=True)
        )
        
        # Get all existing attachment IDs for this conversation to avoid processing duplicates
        existing_attachment_ids = set(
            EmailAttachment.objects.filter(
                email_message__conversation=conversation
            ).values_list('gmail_attachment_id', flat=True)
        )
        
        # Also get existing attachments based on file content (filename + content_type + size)
        # This prevents storing the same file multiple times when Gmail creates new attachment IDs for replies
        existing_attachment_content = set()
        existing_attachments = EmailAttachment.objects.filter(
            email_message__conversation=conversation
        ).values('file_name', 'content_type', 'size_bytes')
        
        for att in existing_attachments:
            if att['file_name'] and att['content_type'] and att['size_bytes']:
                content_key = f"{att['file_name']}_{att['content_type']}_{att['size_bytes']}"
                existing_attachment_content.add(content_key)
        
        # Fetch thread messages from Gmail API (this is fast - just gets message IDs)
        try:
            thread_data = svc.get_thread_messages(cred, conversation.gmail_thread_id)
            thread_messages = thread_data.get('messages', [])
        except Exception as e:
            logger.error(f"Error fetching Gmail thread messages: {str(e)}")
            return {
                'success': False,
                'message': f"Failed to fetch Gmail thread messages: {str(e)}"
            }
        
        # Quick check: if all messages already exist, we might still need to update bodies
        thread_message_ids = {msg.get('id') for msg in thread_messages}
        all_messages_exist = thread_message_ids.issubset(existing_message_ids)
        
        # If all messages exist but some have empty bodies, we should still process for body updates
        if all_messages_exist and not messages_needing_body_update:
            return {
                'success': True,
                'message': 'All messages already synced',
                'data': {
                    'conversation_id': conversation_id,
                    'thread_id': conversation.gmail_thread_id,
                    'new_messages_count': 0,
                    'skipped_messages_count': len(thread_messages),
                    'new_attachments_count': 0,
                    'updated_bodies_count': 0,
                    'total_messages_in_thread': len(thread_messages)
                }
            }
        
        # Process only new messages (much faster!)
        new_messages_count = 0
        new_attachments_count = 0
        skipped_messages_count = 0
        
        for gmail_message in thread_messages:
            gmail_message_id = gmail_message.get('id')
            
            # Skip if message already exists
            if gmail_message_id in existing_message_ids:
                skipped_messages_count += 1
                continue
            
            # This is a new message - process it
            try:
                message_details = svc.get_message_details(cred, gmail_message_id)
                
                # Extract headers
                headers = message_details.get('payload', {}).get('headers', [])
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
                from_email = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
                to_email = next((h['value'] for h in headers if h['name'].lower() == 'to'), '')
                date_header = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
                
                # Clean emoji and special characters from text fields
                import re
                subject = re.sub(r'[^\x00-\x7F]+', '', subject)
                from_email = re.sub(r'[^\x00-\x7F]+', '', from_email)
                to_email = re.sub(r'[^\x00-\x7F]+', '', to_email)
                
                # Parse sent date
                sent_at = None
                if date_header:
                    try:
                        from email.utils import parsedate_to_datetime
                        sent_at = parsedate_to_datetime(date_header)
                    except:
                        pass
                
                # Extract body - comprehensive extraction for all Gmail message structures
                body = ''
                payload = message_details.get('payload', {})
                
                def extract_body_from_payload(payload_obj):
                    """Recursively extract body content from Gmail message payload"""
                    nonlocal body
                    
                    # If we already found a body, don't overwrite it
                    if body:
                        return
                    
                    # Check if this payload has a body with data
                    if payload_obj.get('body', {}).get('data'):
                        try:
                            import base64
                            content = base64.urlsafe_b64decode(payload_obj['body']['data']).decode('utf-8')
                            content = re.sub(r'[^\x00-\x7F]+', '', content)
                            if content.strip():
                                body = content
                                return
                        except (UnicodeDecodeError, Exception):
                            try:
                                content = base64.urlsafe_b64decode(payload_obj['body']['data']).decode('ascii', errors='ignore')
                                content = re.sub(r'[^\x00-\x7F]+', '', content)
                                if content.strip():
                                    body = content
                                    return
                            except Exception:
                                pass
                    
                    # Check if this payload has parts
                    if payload_obj.get('parts'):
                        for part in payload_obj['parts']:
                            # Prefer text/plain over text/html
                            if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                                try:
                                    content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                                    content = re.sub(r'[^\x00-\x7F]+', '', content)
                                    if content.strip():
                                        body = content
                                        return
                                except (UnicodeDecodeError, Exception):
                                    try:
                                        content = base64.urlsafe_b64decode(part['body']['data']).decode('ascii', errors='ignore')
                                        content = re.sub(r'[^\x00-\x7F]+', '', content)
                                        if content.strip():
                                            body = content
                                            return
                                    except Exception:
                                        pass
                            
                            # If no text/plain found, try text/html
                            elif part.get('mimeType') == 'text/html' and part.get('body', {}).get('data') and not body:
                                try:
                                    content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                                    content = re.sub(r'[^\x00-\x7F]+', '', content)
                                    if content.strip():
                                        body = content
                                        return
                                except (UnicodeDecodeError, Exception):
                                    try:
                                        content = base64.urlsafe_b64decode(part['body']['data']).decode('ascii', errors='ignore')
                                        content = re.sub(r'[^\x00-\x7F]+', '', content)
                                        if content.strip():
                                            body = content
                                            return
                                    except Exception:
                                        pass
                            
                            # Recursively check nested parts
                            elif part.get('parts'):
                                extract_body_from_payload(part)
                
                # Extract body from the main payload
                extract_body_from_payload(payload)
                
                # If still no body found, try alternative extraction methods
                if not body:
                    # Try to get body from the message snippet if available
                    snippet = message_details.get('snippet', '')
                    if snippet:
                        body = re.sub(r'[^\x00-\x7F]+', '', snippet)
                    
                    # If still no body, try to extract from any text part
                    def find_any_text_content(payload_obj):
                        nonlocal body
                        if body:
                            return
                        
                        if payload_obj.get('body', {}).get('data'):
                            try:
                                content = base64.urlsafe_b64decode(payload_obj['body']['data']).decode('utf-8', errors='ignore')
                                content = re.sub(r'[^\x00-\x7F]+', '', content)
                                if content.strip():
                                    body = content
                                    return
                            except Exception:
                                pass
                        
                        if payload_obj.get('parts'):
                            for part in payload_obj['parts']:
                                if part.get('mimeType', '').startswith('text/') and part.get('body', {}).get('data'):
                                    try:
                                        content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                                        content = re.sub(r'[^\x00-\x7F]+', '', content)
                                        if content.strip():
                                            body = content
                                            return
                                    except Exception:
                                        pass
                                elif part.get('parts'):
                                    find_any_text_content(part)
                    
                    find_any_text_content(payload)
                
                # Clean up the body content - remove quoted replies and email metadata
                if body:
                    def clean_email_body(content):
                        """Clean email body by removing quoted replies and metadata"""
                        if not content:
                            return content
                        
                        # Remove HTML entities first
                        content = re.sub(r'&[a-zA-Z]+;', '', content)
                        
                        # Handle single-line content by splitting on common reply patterns
                        if '\n' not in content or content.count('\n') < 2:
                            # For single-line content, try to extract just the first part before reply indicators
                            patterns_to_remove = [
                                r' On .+ at \d+:\d+, .+ wrote:.*',
                                r' On .+, .+ wrote:.*',
                                r' From: .+ <.+@.+>.*',
                                r' To: .+ <.+@.+>.*',
                                r' Subject: .+.*',
                                r' Date: .+.*',
                                r' Sent: .+.*',
                                r' Cc: .+.*',
                                r' Bcc: .+.*',
                                r' >.*',
                                r' [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}.*'
                            ]
                            
                            cleaned_content = content
                            for pattern in patterns_to_remove:
                                cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.IGNORECASE)
                            
                            # Remove extra whitespace
                            cleaned_content = re.sub(r'\s+', ' ', cleaned_content)
                            return cleaned_content.strip()
                        
                        # For multi-line content, process line by line
                        lines = content.split('\n')
                        cleaned_lines = []
                        in_quoted_section = False
                        
                        for line in lines:
                            line_stripped = line.strip()
                            
                            # Skip empty lines
                            if not line_stripped:
                                continue
                            
                            # Check if this line starts a quoted section
                            if (line_stripped.startswith('On ') and 'wrote:' in line_stripped or
                                line_stripped.startswith('>') or
                                line_stripped.startswith('From:') or
                                line_stripped.startswith('To:') or
                                line_stripped.startswith('Subject:') or
                                line_stripped.startswith('Date:') or
                                line_stripped.startswith('Sent:') or
                                line_stripped.startswith('Cc:') or
                                line_stripped.startswith('Bcc:') or
                                re.match(r'^On .+ at \d+:\d+, .+ wrote:$', line_stripped) or
                                re.match(r'^On .+, .+ wrote:$', line_stripped) or
                                re.match(r'^From: .+ <.+@.+>$', line_stripped) or
                                re.match(r'^To: .+ <.+@.+>$', line_stripped) or
                                re.match(r'^Subject: .+$', line_stripped) or
                                re.match(r'^Date: .+$', line_stripped) or
                                re.match(r'^Sent: .+$', line_stripped)):
                                in_quoted_section = True
                                continue
                            
                            # If we're in a quoted section, skip lines that look like email addresses
                            if in_quoted_section:
                                if (re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', line_stripped) or
                                    line_stripped in ['&lt;', '&gt;', '&amp;', '&quot;', '&apos;']):
                                    continue
                            
                            # Add the line if it's not in a quoted section or if it's meaningful content
                            if not in_quoted_section:
                                cleaned_lines.append(line)
                        
                        # Join the cleaned lines
                        cleaned_content = '\n'.join(cleaned_lines).strip()
                        
                        # Remove extra whitespace
                        cleaned_content = re.sub(r'\s+', ' ', cleaned_content)
                        
                        return cleaned_content.strip()
                    
                    # Clean the extracted body
                    body = clean_email_body(body)
                
                # Extract attachments (only new ones)
                attachments = []
                def extract_attachments_from_parts(parts):
                    for part in parts:
                        if part.get('filename') and part.get('body', {}).get('attachmentId'):
                            attachment_id = part.get('body', {}).get('attachmentId')
                            filename = part.get('filename', '')
                            mime_type = part.get('mimeType', '')
                            size = part.get('body', {}).get('size', 0)
                            
                            # Check both attachment ID and content duplicates
                            content_key = f"{filename}_{mime_type}_{size}"
                            is_duplicate = (
                                attachment_id in existing_attachment_ids or 
                                content_key in existing_attachment_content
                            )
                            
                            if not is_duplicate:
                                attachment_info = {
                                    'filename': filename,
                                    'mimeType': mime_type,
                                    'size': size,
                                    'attachmentId': attachment_id,
                                    'is_image': mime_type.startswith('image/')
                                }
                                attachments.append(attachment_info)
                        elif part.get('parts'):
                            extract_attachments_from_parts(part['parts'])
                
                if payload.get('parts'):
                    extract_attachments_from_parts(payload['parts'])
                elif payload.get('filename') and payload.get('body', {}).get('attachmentId'):
                    attachment_id = payload.get('body', {}).get('attachmentId')
                    filename = payload.get('filename', '')
                    mime_type = payload.get('mimeType', '')
                    size = payload.get('body', {}).get('size', 0)
                    
                    # Check both attachment ID and content duplicates
                    content_key = f"{filename}_{mime_type}_{size}"
                    is_duplicate = (
                        attachment_id in existing_attachment_ids or 
                        content_key in existing_attachment_content
                    )
                    
                    if not is_duplicate:
                        attachment_info = {
                            'filename': filename,
                            'mimeType': mime_type,
                            'size': size,
                            'attachmentId': attachment_id,
                            'is_image': mime_type.startswith('image/')
                        }
                        attachments.append(attachment_info)
                
                # Basic validation to ensure data is safe for database
                try:
                    subject = str(subject)[:1000] if subject else ''
                    from_email = str(from_email)[:500] if from_email else ''
                    to_email = str(to_email)[:500] if to_email else ''
                    body = str(body)[:10000] if body else ''
                    
                    # Normalize email formats to ensure consistency
                    def normalize_email_format(email_string):
                        """Normalize email format to extract just the email address"""
                        if not email_string:
                            return ""
                        
                        email_string = email_string.strip()
                        
                        # Handle "Name <email@domain.com>" format
                        if "<" in email_string and ">" in email_string:
                            start = email_string.find("<") + 1
                            end = email_string.find(">")
                            if start < end:
                                return email_string[start:end].strip().lower()
                        
                        # Handle raw email format
                        return email_string.lower()
                    
                    # Normalize email formats
                    from_email = normalize_email_format(from_email)
                    to_email = normalize_email_format(to_email)
                    
                    # Clean attachment data
                    for attachment_info in attachments:
                        attachment_info['filename'] = str(attachment_info['filename'])[:255] if attachment_info['filename'] else ''
                        attachment_info['mimeType'] = str(attachment_info['mimeType'])[:100] if attachment_info['mimeType'] else ''
                        attachment_info['attachmentId'] = str(attachment_info['attachmentId'])[:500] if attachment_info['attachmentId'] else ''
                    
                except Exception as e:
                    logger.error(f"Error cleaning message data for {gmail_message_id}: {str(e)}")
                    continue
                
                # Create new message record (incoming messages are unseen until user opens conversation)
                email_message = EmailChatMessage.objects.create(
                    conversation=conversation,
                    gmail_message_id=gmail_message_id,
                    gmail_thread_id=conversation.gmail_thread_id,
                    from_email=from_email,
                    to_email=to_email,
                    subject=subject,
                    body=body,
                    sent_at=sent_at,
                    first_message_id=thread_messages[0].get('id') if thread_messages else None,
                    is_seen=False,
                )
                new_messages_count += 1
                
                # Handle attachments for new message
                for attachment_info in attachments:
                    attachment, created = EmailAttachment.objects.get_or_create(
                        email_message=email_message,
                        gmail_attachment_id=attachment_info['attachmentId'],
                        defaults={
                            'file_name': attachment_info['filename'],
                            'file_url': f"gmail://{gmail_message_id}/{attachment_info['attachmentId']}",  # Set proper gmail:// format
                            'content_type': attachment_info['mimeType'],
                            'size_bytes': attachment_info['size'],
                            'is_image': attachment_info['is_image']
                        }
                    )
                    
                    # Download and upload to S3 if it's a new attachment OR if existing attachment still has Gmail URL
                    should_upload_to_s3 = (
                        (created and attachment_info['attachmentId']) or  # New attachment
                        (not created and attachment.file_url and attachment.file_url.startswith('gmail://') and attachment_info['attachmentId'])  # Existing attachment with Gmail URL
                    )
                    
                    if should_upload_to_s3:
                        if created:
                            logger.info(f"[DOCUMENT_SYNC] Processing NEW attachment: {attachment_info['filename']}")
                        else:
                            logger.info(f"[DOCUMENT_SYNC] Processing EXISTING attachment with Gmail URL: {attachment_info['filename']} (current URL: {attachment.file_url})")
                        
                        try:
                            # Fetch attachment data from Gmail
                            attachment_data = svc.get_attachment(cred, gmail_message_id, attachment_info['attachmentId'])
                            
                            if attachment_data and attachment_data.get('data'):
                                import base64
                                
                                # Check if S3PresignedService is available
                                try:
                                    from envoy.services.s3_presigned_service import S3PresignedService
                                    logger.info(f"[DOCUMENT_SYNC] S3PresignedService imported successfully")
                                except ImportError as e:
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Failed to import S3PresignedService: {e}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Import error details: {type(e).__name__}: {str(e)}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Attachment will remain with Gmail URL: {attachment.file_url}")
                                    continue
                                except Exception as e:
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Unexpected error importing S3PresignedService: {e}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Error type: {type(e).__name__}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Attachment will remain with Gmail URL: {attachment.file_url}")
                                    continue
                                
                                # Decode the attachment data
                                file_data = base64.urlsafe_b64decode(attachment_data['data'])
                                
                                # Generate folder path for organization
                                folder_path = f"attachments/{conversation.id}/{email_message.id}"
                                
                                # Debug: Log environment configuration
                                import os
                                logger.info(f"[DOCUMENT_SYNC] Environment check for {attachment_info['filename']}:")
                                logger.info(f"[DOCUMENT_SYNC] - S3_ACCESS_KEY_ID: {'Set' if os.getenv('S3_ACCESS_KEY_ID') else 'Not set'}")
                                logger.info(f"[DOCUMENT_SYNC] - S3_SECRET_ACCESS_KEY: {'Set' if os.getenv('S3_SECRET_ACCESS_KEY') else 'Not set'}")
                                logger.info(f"[DOCUMENT_SYNC] - S3_BUCKET_NAME: {'Set' if os.getenv('S3_BUCKET_NAME') else 'Not set'}")
                                logger.info(f"[DOCUMENT_SYNC] - S3_REGION: {'Set' if os.getenv('S3_REGION') else 'Not set'}")
                                logger.info(f"[DOCUMENT_SYNC] - CDN_BASE_URL: {'Set' if os.getenv('CDN_BASE_URL') else 'Not set'}")
                                logger.info(f"[DOCUMENT_SYNC] - File size: {len(file_data)} bytes")
                                logger.info(f"[DOCUMENT_SYNC] - Folder path: {folder_path}")
                                
                                # Check if all required S3 environment variables are set
                                required_s3_vars = ['S3_ACCESS_KEY_ID', 'S3_SECRET_ACCESS_KEY', 'S3_BUCKET_NAME', 'S3_REGION']
                                missing_vars = [var for var in required_s3_vars if not os.getenv(var)]
                                if missing_vars:
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Missing required S3 environment variables: {missing_vars}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Cannot upload to S3, attachment will remain with Gmail URL: {attachment.file_url}")
                                    continue
                                
                                # Test S3PresignedService instantiation
                                try:
                                    # Try to get the S3 client to test credentials
                                    s3_client = S3PresignedService._get_client()
                                    logger.info(f"[DOCUMENT_SYNC] ✅ S3PresignedService client created successfully")
                                except Exception as client_error:
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Failed to create S3PresignedService client: {client_error}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Client error type: {type(client_error).__name__}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Attachment will remain with Gmail URL: {attachment.file_url}")
                                    continue
                                
                                # Upload to S3 using presigned service
                                try:
                                    upload_result = S3PresignedService.upload_file_to_s3(
                                        file_content=file_data,
                                        file_name=attachment_info['filename'],
                                        folder=folder_path
                                    )
                                    
                                    # Debug: Log upload result details
                                    logger.info(f"[DOCUMENT_SYNC] Upload result for {attachment_info['filename']}: {upload_result}")
                                    
                                except Exception as upload_error:
                                    logger.error(f"[DOCUMENT_SYNC] ❌ S3 upload failed for {attachment_info['filename']}: {upload_error}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Upload error type: {type(upload_error).__name__}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Upload error details: {str(upload_error)}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Attachment will remain with Gmail URL: {attachment.file_url}")
                                    continue
                                
                                if upload_result and upload_result.get('file_key'):
                                    # Get S3 key from upload result
                                    s3_key = upload_result["file_key"]
                                    
                                    # Construct CDN URL using CDN_BASE_URL
                                    import os
                                    cdn_base_url = os.getenv("CDN_BASE_URL")
                                    
                                    logger.info(f"[DOCUMENT_SYNC] Processing attachment {attachment_info['filename']} for conversation {conversation_id}")
                                    logger.info(f"[DOCUMENT_SYNC] S3 key: {s3_key}")
                                    logger.info(f"[DOCUMENT_SYNC] CDN_BASE_URL configured: {'Yes' if cdn_base_url else 'No'}")
                                    
                                    if cdn_base_url:
                                        cdn_url = f"{cdn_base_url.rstrip('/')}/{s3_key}"
                                        # Update attachment with CDN URL
                                        attachment.file_url = cdn_url
                                        attachment.save()
                                        
                                        logger.info(f"[DOCUMENT_SYNC] ✅ Uploaded attachment {attachment_info['filename']} to S3: {s3_key}")
                                        logger.info(f"[DOCUMENT_SYNC] ✅ CDN URL constructed: {cdn_url}")
                                        logger.info(f"[DOCUMENT_SYNC] ✅ CDN key functionality working properly")
                                        logger.info(f"[DOCUMENT_SYNC] ✅ Attachment URL updated from Gmail to CDN: {attachment.file_url}")
                                    else:
                                        # Fallback to presigned URL if CDN_BASE_URL not configured
                                        attachment.file_url = upload_result['file_url']
                                        attachment.save()
                                        
                                        logger.info(f"[DOCUMENT_SYNC] ⚠️ Uploaded attachment {attachment_info['filename']} to S3: {s3_key}")
                                        logger.warning(f"[DOCUMENT_SYNC] ⚠️ CDN_BASE_URL not configured, using presigned URL: {upload_result['file_url']}")
                                        logger.info(f"[DOCUMENT_SYNC] ⚠️ Attachment URL updated from Gmail to S3 presigned: {attachment.file_url}")
                                else:
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Failed to upload attachment {attachment_info['filename']} to S3")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Upload result: {upload_result}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Attachment will remain with Gmail URL: {attachment.file_url}")
                                    
                            else:
                                logger.warning(f"Could not fetch attachment data for {attachment_info['filename']}")
                                
                        except Exception as e:
                            logger.error(f"Error uploading attachment {attachment_info['filename']} to S3: {str(e)}")
                            logger.error(f"Exception type: {type(e).__name__}")
                            logger.error(f"Exception details: {e}")
                            import traceback
                            logger.error(f"Traceback: {traceback.format_exc()}")
                            logger.error(f"Attachment will remain with Gmail URL: {attachment.file_url}")
                            # Continue with other attachments even if one fails
                    
                    if created:
                        new_attachments_count += 1
                        logger.info(f"Added new attachment {attachment_info['filename']} to message {gmail_message_id}")
                    else:
                        if attachment.file_url and not attachment.file_url.startswith('gmail://'):
                            logger.info(f"Attachment {attachment_info['filename']} already exists with CDN URL: {attachment.file_url}")
                        else:
                            logger.info(f"Attachment {attachment_info['filename']} already exists with Gmail URL: {attachment.file_url}")
                
                # Log if any attachments were skipped due to content duplicates
                if len(attachments) == 0 and message_details.get('payload', {}).get('parts'):
                    # Check if there were attachments but they were all duplicates
                    total_attachments_in_message = 0
                    def count_attachments_in_parts(parts):
                        nonlocal total_attachments_in_message
                        for part in parts:
                            if part.get('filename') and part.get('body', {}).get('attachmentId'):
                                total_attachments_in_message += 1
                            elif part.get('parts'):
                                count_attachments_in_parts(part['parts'])
                    
                    count_attachments_in_parts(message_details.get('payload', {}).get('parts', []))
                    if total_attachments_in_message > 0:
                        logger.info(f"Skipped {total_attachments_in_message} duplicate attachments in message {gmail_message_id} (same files already exist in conversation)")
                
            except Exception as e:
                logger.error(f"Error processing new message {gmail_message_id}: {str(e)}")
                continue
        
        # Update existing messages that have empty bodies
        updated_bodies_count = 0
        if messages_needing_body_update:
            logger.info(f"Found {len(messages_needing_body_update)} messages with empty bodies, attempting to update them")
            
            for gmail_message_id in messages_needing_body_update:
                try:
                    # Get the existing message
                    existing_message = EmailChatMessage.objects.get(
                        conversation=conversation,
                        gmail_message_id=gmail_message_id
                    )
                    
                    # Skip if body is already populated
                    if existing_message.body and existing_message.body.strip():
                        continue
                    
                    # Fetch fresh message details from Gmail
                    message_details = svc.get_message_details(cred, gmail_message_id)
                    
                    # Extract body using the same comprehensive logic
                    body = ''
                    payload = message_details.get('payload', {})
                    
                    # Import re module for text cleaning
                    import re
                    
                    def extract_body_from_payload_for_update(payload_obj):
                        """Recursively extract body content from Gmail message payload for updates"""
                        nonlocal body
                        
                        if body:
                            return
                        
                        # Check if this payload has a body with data
                        if payload_obj.get('body', {}).get('data'):
                            try:
                                import base64
                                content = base64.urlsafe_b64decode(payload_obj['body']['data']).decode('utf-8')
                                content = re.sub(r'[^\x00-\x7F]+', '', content)
                                if content.strip():
                                    body = content
                                    return
                            except (UnicodeDecodeError, Exception):
                                try:
                                    content = base64.urlsafe_b64decode(payload_obj['body']['data']).decode('ascii', errors='ignore')
                                    content = re.sub(r'[^\x00-\x7F]+', '', content)
                                    if content.strip():
                                        body = content
                                        return
                                except Exception:
                                    pass
                        
                        # Check if this payload has parts
                        if payload_obj.get('parts'):
                            for part in payload_obj['parts']:
                                # Prefer text/plain over text/html
                                if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                                    try:
                                        content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                                        content = re.sub(r'[^\x00-\x7F]+', '', content)
                                        if content.strip():
                                            body = content
                                            return
                                    except (UnicodeDecodeError, Exception):
                                        try:
                                            content = base64.urlsafe_b64decode(part['body']['data']).decode('ascii', errors='ignore')
                                            content = re.sub(r'[^\x00-\x7F]+', '', content)
                                            if content.strip():
                                                body = content
                                                return
                                        except Exception:
                                            pass
                                
                                # If no text/plain found, try text/html
                                elif part.get('mimeType') == 'text/html' and part.get('body', {}).get('data') and not body:
                                    try:
                                        content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                                        content = re.sub(r'[^\x00-\x7F]+', '', content)
                                        if content.strip():
                                            body = content
                                            return
                                    except (UnicodeDecodeError, Exception):
                                        try:
                                            content = base64.urlsafe_b64decode(part['body']['data']).decode('ascii', errors='ignore')
                                            content = re.sub(r'[^\x00-\x7F]+', '', content)
                                            if content.strip():
                                                body = content
                                                return
                                        except Exception:
                                            pass
                                
                                # Recursively check nested parts
                                elif part.get('parts'):
                                    extract_body_from_payload_for_update(part)
                    
                    # Extract body from the main payload
                    extract_body_from_payload_for_update(payload)
                    
                    # If still no body found, try alternative extraction methods
                    if not body:
                        # Try to get body from the message snippet if available
                        snippet = message_details.get('snippet', '')
                        if snippet:
                            body = re.sub(r'[^\x00-\x7F]+', '', snippet)
                        
                        # If still no body, try to extract from any text part
                        def find_any_text_content_for_update(payload_obj):
                            nonlocal body
                            if body:
                                return
                            
                            if payload_obj.get('body', {}).get('data'):
                                try:
                                    content = base64.urlsafe_b64decode(payload_obj['body']['data']).decode('utf-8', errors='ignore')
                                    content = re.sub(r'[^\x00-\x7F]+', '', content)
                                    if content.strip():
                                        body = content
                                        return
                                except Exception:
                                    pass
                            
                            if payload_obj.get('parts'):
                                for part in payload_obj['parts']:
                                    if part.get('mimeType', '').startswith('text/') and part.get('body', {}).get('data'):
                                        try:
                                            content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                                            content = re.sub(r'[^\x00-\x7F]+', '', content)
                                            if content.strip():
                                                body = content
                                                return
                                        except Exception:
                                            pass
                                    elif part.get('parts'):
                                        find_any_text_content_for_update(part)
                        
                        find_any_text_content_for_update(payload)
                    
                    # Clean up the body content - remove quoted replies and email metadata
                    if body:
                        def clean_email_body_for_update(content):
                            """Clean email body by removing quoted replies and metadata"""
                            if not content:
                                return content
                            
                            # Remove HTML entities first
                            content = re.sub(r'&[a-zA-Z]+;', '', content)
                            
                            # Handle single-line content by splitting on common reply patterns
                            if '\n' not in content or content.count('\n') < 2:
                                # For single-line content, try to extract just the first part before reply indicators
                                patterns_to_remove = [
                                    r' On .+ at \d+:\d+, .+ wrote:.*',
                                    r' On .+, .+ wrote:.*',
                                    r' From: .+ <.+@.+>.*',
                                    r' To: .+ <.+@.+>.*',
                                    r' Subject: .+.*',
                                    r' Date: .+.*',
                                    r' Sent: .+.*',
                                    r' Cc: .+.*',
                                    r' Bcc: .+.*',
                                    r' >.*',
                                    r' [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}.*'
                                ]
                                
                                cleaned_content = content
                                for pattern in patterns_to_remove:
                                    cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.IGNORECASE)
                                
                                # Remove extra whitespace
                                cleaned_content = re.sub(r'\s+', ' ', cleaned_content)
                                return cleaned_content.strip()
                            
                            # For multi-line content, process line by line
                            lines = content.split('\n')
                            cleaned_lines = []
                            in_quoted_section = False
                            
                            for line in lines:
                                line_stripped = line.strip()
                                
                                # Skip empty lines
                                if not line_stripped:
                                    continue
                                
                                # Check if this line starts a quoted section
                                if (line_stripped.startswith('On ') and 'wrote:' in line_stripped or
                                    line_stripped.startswith('>') or
                                    line_stripped.startswith('From:') or
                                    line_stripped.startswith('To:') or
                                    line_stripped.startswith('Subject:') or
                                    line_stripped.startswith('Date:') or
                                    line_stripped.startswith('Sent:') or
                                    line_stripped.startswith('Cc:') or
                                    line_stripped.startswith('Bcc:') or
                                    re.match(r'^On .+ at \d+:\d+, .+ wrote:$', line_stripped) or
                                    re.match(r'^On .+, .+ wrote:$', line_stripped) or
                                    re.match(r'^From: .+ <.+@.+>$', line_stripped) or
                                    re.match(r'^To: .+ <.+@.+>$', line_stripped) or
                                    re.match(r'^Subject: .+$', line_stripped) or
                                    re.match(r'^Date: .+$', line_stripped) or
                                    re.match(r'^Sent: .+$', line_stripped)):
                                    in_quoted_section = True
                                    continue
                                
                                # If we're in a quoted section, skip lines that look like email addresses
                                if in_quoted_section:
                                    if (re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', line_stripped) or
                                        line_stripped in ['&lt;', '&gt;', '&amp;', '&quot;', '&apos;']):
                                        continue
                                
                                # Add the line if it's not in a quoted section or if it's meaningful content
                                if not in_quoted_section:
                                    cleaned_lines.append(line)
                            
                            # Join the cleaned lines
                            cleaned_content = '\n'.join(cleaned_lines).strip()
                            
                            # Remove extra whitespace
                            cleaned_content = re.sub(r'\s+', ' ', cleaned_content)
                            
                            return cleaned_content.strip()
                        
                        # Clean the extracted body
                        body = clean_email_body_for_update(body)
                    
                    # Update the message body if we found content
                    if body and body.strip():
                        existing_message.body = body[:10000]  # Limit to 10k characters
                        existing_message.save()
                        updated_bodies_count += 1
                        logger.info(f"Updated body for message {gmail_message_id}")
                    
                except Exception as e:
                    logger.error(f"Error updating body for message {gmail_message_id}: {str(e)}")
                    continue
        
        logger.info(f"Synced Gmail thread for conversation {conversation_id}: {new_messages_count} new messages, {skipped_messages_count} skipped (already stored), {new_attachments_count} new attachments, {updated_bodies_count} bodies updated")
        
        return {
            'success': True,
            'message': f"Successfully synced {new_messages_count} new messages, skipped {skipped_messages_count} existing messages, added {new_attachments_count} new attachments, and updated {updated_bodies_count} message bodies",
            'data': {
                'conversation_id': conversation_id,
                'thread_id': conversation.gmail_thread_id,
                'new_messages_count': new_messages_count,
                'skipped_messages_count': skipped_messages_count,
                'new_attachments_count': new_attachments_count,
                'updated_bodies_count': updated_bodies_count,
                'total_messages_in_thread': len(thread_messages)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in sync_gmail_thread_messages: {str(e)}")
        return {
            'success': False,
            'message': f"Internal error during thread sync: {str(e)}"
        }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chatmail_conversations(request):
    """Get all chatmail conversations with unread (unseen) message count per conversation."""
    try:
        from django.db.models import Count, Q

        user_id = request.GET.get('user_id')
        conversation_type = request.GET.get('conversation_type')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        conversations = ChatConversation.objects.all()
        
        if user_id:
            conversations = conversations.filter(user_id=user_id)
        
        if conversation_type:
            conversations = conversations.filter(type=conversation_type)
        
        # Annotate unread count: messages where is_seen=False (new messages received)
        conversations = conversations.select_related('user', 'insurer').annotate(
            unread_count=Count('messages', filter=Q(messages__is_seen=False), distinct=True)
        ).order_by('-created_at')
        
        # Paginate results
        total_count = conversations.count()
        start = (page - 1) * page_size
        end = start + page_size
        paginated_conversations = conversations[start:end]
        
        conversation_data = []
        for conversation in paginated_conversations:
            unread = getattr(conversation, 'unread_count', 0) or 0
            conversation_data.append({
                'id': conversation.id,
                'code': conversation.code,
                'type': conversation.type,
                'type_based_id': conversation.type_based_id,
                'insurer_id': conversation.insurer_id,
                'insurer_name': conversation.insurer.name if conversation.insurer else None,
                'user_id': conversation.user_id,
                'user_name': conversation.user.display_name if conversation.user else None,
                'gmail_thread_id': conversation.gmail_thread_id,
                'created_at': conversation.created_at,
                'message_count': conversation.messages.count(),
                'unread_count': unread,
                'has_new_messages': unread > 0,
            })
        
        return Response(
            {
                "success": True,
                "message": "Conversations retrieved successfully",
                "data": {
                    'conversations': conversation_data,
                    'pagination': {
                        'page': page,
                        'page_size': page_size,
                        'total_count': total_count,
                        'total_pages': (total_count + page_size - 1) // page_size
                    }
                }
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error in get_chatmail_conversations: {str(e)}")
        return Response(
            {
                "error": "Internal server error",
                "message": f"Internal server error: {str(e)}",
                "error_code": "INTERNAL_SERVER_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_conversation_seen(request):
    """
    Mark all messages in a conversation as seen (read).
    Call this when the user opens a conversation so unread_count goes to zero.
    """
    try:
        conversation_id = request.data.get('conversation_id')
        if not conversation_id:
            return Response(
                {
                    "error": "Missing required field",
                    "message": "conversation_id is required",
                    "error_code": "MISSING_CONVERSATION_ID",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            conversation = ChatConversation.objects.get(id=conversation_id)
        except ChatConversation.DoesNotExist:
            return Response(
                {
                    "error": "Not found",
                    "message": f"Conversation with id {conversation_id} not found",
                    "error_code": "CONVERSATION_NOT_FOUND",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        updated = EmailChatMessage.objects.filter(conversation=conversation, is_seen=False).update(is_seen=True)
        return Response(
            {
                "success": True,
                "message": "Conversation marked as seen",
                "data": {
                    "conversation_id": conversation_id,
                    "messages_marked_seen": updated,
                },
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error in mark_conversation_seen: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Internal server error",
                "message": str(e),
                "error_code": "INTERNAL_SERVER_ERROR",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_attachment(request):
    """
    Download/access attachment file from S3 or local storage.
    This endpoint serves files from S3/CDN or falls back to local storage.
    """
    try:
        attachment_id = request.GET.get('attachment_id')
        
        if not attachment_id:
            return Response(
                {
                    "error": "Missing required field",
                    "message": "attachment_id is required",
                    "error_code": "MISSING_ATTACHMENT_ID"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the attachment record
        try:
            attachment = EmailAttachment.objects.get(id=attachment_id)
        except EmailAttachment.DoesNotExist:
            return Response(
                {
                    "error": "Attachment not found",
                    "message": f"Attachment with ID {attachment_id} not found",
                    "error_code": "ATTACHMENT_NOT_FOUND"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if file is stored in S3 with CDN URL
        if attachment.file_url and attachment.file_url.startswith('https://'):
            # Redirect to CDN URL for direct access
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(attachment.file_url)
        
        # Fallback to local file storage
        if attachment.file and attachment.file.name:
            from django.http import FileResponse
            
            try:
                # Open and serve the local file
                file_handle = attachment.file.open('rb')
                response = FileResponse(file_handle, content_type=attachment.content_type)
                
                # Set appropriate headers
                if attachment.is_image:
                    # For images, display in browser
                    response['Content-Disposition'] = f'inline; filename="{attachment.file_name}"'
                else:
                    # For other files, download
                    response['Content-Disposition'] = f'attachment; filename="{attachment.file_name}"'
                
                response['Content-Length'] = attachment.size_bytes
                
                return response
                
            except Exception as e:
                logger.error(f"Error serving local attachment file: {str(e)}")
                return Response(
                    {
                        "error": "Failed to serve file",
                        "message": f"Failed to serve attachment file: {str(e)}",
                        "error_code": "FILE_SERVE_FAILED"
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # No file found in either S3 or local storage
        return Response(
            {
                "error": "File not found",
                "message": "Attachment file is not available",
                "error_code": "FILE_NOT_FOUND"
            },
            status=status.HTTP_404_NOT_FOUND
        )
            
    except Exception as e:
        logger.error(f"Error in download_attachment: {str(e)}")
        return Response(
            {
                "error": "Internal server error",
                "message": f"Internal server error: {str(e)}",
                "error_code": "INTERNAL_SERVER_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_attachment_info(request):
    """
    Get attachment information without downloading the file.
    This is useful for displaying attachment details in the UI.
    """
    try:
        attachment_id = request.GET.get('attachment_id')
        
        if not attachment_id:
            return Response(
                {
                    "error": "Missing required field",
                    "message": "attachment_id is required",
                    "error_code": "MISSING_ATTACHMENT_ID"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the attachment record
        try:
            attachment = EmailAttachment.objects.select_related('email_message__conversation').get(id=attachment_id)
        except EmailAttachment.DoesNotExist:
            return Response(
                {
                    "error": "Attachment not found",
                    "message": f"Attachment with ID {attachment_id} not found",
                    "error_code": "ATTACHMENT_NOT_FOUND"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Determine file access URLs based on storage location
        if attachment.file_url and attachment.file_url.startswith('https://'):
            # File is stored in S3 with CDN URL - use CDN URL for direct access
            download_url = attachment.file_url
            view_url = attachment.file_url if attachment.is_image else None
            storage_type = "s3_cdn"
        elif attachment.file and attachment.file.name:
            # File is stored locally - use direct media URL
            base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
            direct_url = f"{base_url}{attachment.file.url}"
            download_url = direct_url
            view_url = direct_url if attachment.is_image else None
            storage_type = "local"
        else:
            # Fallback to download endpoint if file not stored anywhere
            base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
            download_url = f"{base_url}/api/chatmail/download-attachment?attachment_id={attachment.id}"
            view_url = download_url if attachment.is_image else None
            storage_type = "unknown"
        
        # Return attachment information
        attachment_info = {
            'id': attachment.id,
            'file_name': attachment.file_name,
            'content_type': attachment.content_type,
            'size_bytes': attachment.size_bytes,
            'is_image': attachment.is_image,
            'created_at': attachment.created_at,
            'file_url': attachment.file_url,  # CDN URL or gmail:// format
            'storage_type': storage_type,  # s3_cdn, local, or unknown
            'download_url': download_url,
            'view_url': view_url,
            'message_info': {
                'message_id': attachment.email_message.id,
                'subject': attachment.email_message.subject,
                'conversation_id': attachment.email_message.conversation.id,
                'conversation_code': attachment.email_message.conversation.code
            }
        }
        
        return Response(
            {
                "success": True,
                "message": "Attachment information retrieved successfully",
                "data": attachment_info
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error in get_attachment_info: {str(e)}")
        return Response(
            {
                "error": "Internal server error",
                "message": f"Internal server error: {str(e)}",
                "error_code": "INTERNAL_SERVER_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
def gmail_push_webhook(request):
    """
    Gmail Push Notification Webhook Handler for Real-time Email Detection.
    
    This endpoint receives push notifications with type, id, and mail.
    It finds conversations for that specific quotation/policy/endorsement and checks for new messages.
    
    Expected payload:
    {
        "type": "quotation" | "policy" | "endorsement",
        "id": <quotation_id | policy_id | endorsement_id>,
        "mail": "envoy.cloud.services@gmail.com"
    }
    
    The endpoint will:
    1. Construct type_based_id (QR-{id}, PR-{id}, or ER-{id})
    2. Find conversations with that type_based_id
    3. Get their gmail_thread_ids
    4. Check those threads for new messages
    5. Send notifications if new insurer messages are found
    """
    try:
        import json
        
        logger.info(f"[GMAIL_WEBHOOK] Received push notification")
        
        # Parse notification data
        notification_data = {}
        if request.body:
            try:
                notification_data = json.loads(request.body.decode('utf-8'))
            except:
                if hasattr(request, 'data') and request.data:
                    notification_data = request.data
        
        logger.info(f"[GMAIL_WEBHOOK] Notification data: {notification_data}")
        
        # Extract required fields from payload
        type_param = notification_data.get('type', '').lower()
        id_param = notification_data.get('id')
        email_address = notification_data.get('mail') or notification_data.get('email')
        
        # Validate required fields
        if not type_param or not id_param:
            logger.warning(f"[GMAIL_WEBHOOK] Missing required fields: type={type_param}, id={id_param}")
            return Response({
                "status": "acknowledged",
                "error": "Missing required fields: type and id are required"
            }, status=status.HTTP_200_OK)
        
        # Validate type
        valid_types = ['quotation', 'policy', 'endorsement']
        if type_param not in valid_types:
            logger.warning(f"[GMAIL_WEBHOOK] Invalid type: {type_param}")
            return Response({
                "status": "acknowledged",
                "error": f"Invalid type. Must be one of: {', '.join(valid_types)}"
            }, status=status.HTTP_200_OK)
        
        # Construct type_based_id based on type
        type_prefix_map = {
            'quotation': 'QR',
            'policy': 'PR',
            'endorsement': 'ER'
        }
        type_prefix = type_prefix_map[type_param]
        type_based_id = f"{type_prefix}-{id_param}"
        
        logger.info(f"[GMAIL_WEBHOOK] Processing notification for type={type_param}, id={id_param}, type_based_id={type_based_id}")
        
        # Get email address (use provided mail or default to system email)
        SYSTEM_EMAIL = "envoy.cloud.services@gmail.com"
        if not email_address:
            email_address = SYSTEM_EMAIL
            logger.info(f"[GMAIL_WEBHOOK] Using default system email: {email_address}")
        
        # Get Gmail credential for the email
        try:
            cred = GmailCredential.objects.get(system_email=email_address)
        except GmailCredential.DoesNotExist:
            logger.warning(f"[GMAIL_WEBHOOK] No Gmail credential found for {email_address}")
            return Response({
                "status": "acknowledged",
                "error": f"No Gmail credential found for {email_address}"
            }, status=status.HTTP_200_OK)
        
        # Find conversations for this type_based_id
        try:
            conversations = ChatConversation.objects.filter(
                type_based_id=type_based_id
            ).exclude(
                gmail_thread_id__isnull=True
            ).exclude(
                gmail_thread_id=''
            ).select_related('user', 'insurer')
            
            if not conversations.exists():
                logger.info(f"[GMAIL_WEBHOOK] No conversations found for type_based_id: {type_based_id}")
                return Response({
                    "status": "acknowledged",
                    "type": type_param,
                    "id": id_param,
                    "type_based_id": type_based_id,
                    "conversations": [],
                    "message": f"No conversations found for {type_param} {id_param}"
                }, status=status.HTTP_200_OK)
            
            logger.info(f"[GMAIL_WEBHOOK] Found {conversations.count()} conversations for type_based_id: {type_based_id}")
            
            # Process each conversation - check if thread has new messages
            synced_conversations = set()
            conversations_details = []  # Track conversation details with new message counts
            notifications_sent = 0
            
            for conversation in conversations:
                try:
                    # Avoid syncing the same conversation multiple times
                    if conversation.id in synced_conversations:
                        continue
                    
                    if not conversation.gmail_thread_id:
                        logger.debug(f"[GMAIL_WEBHOOK] Conversation {conversation.id} has no gmail_thread_id, skipping")
                        continue
                    
                    logger.info(f"[GMAIL_WEBHOOK] Checking conversation {conversation.id} (thread: {conversation.gmail_thread_id})...")
                    
                    # Sync this conversation - the sync function will check for new messages
                    sync_result = sync_gmail_thread_messages(conversation.id)
                    
                    if sync_result.get('success'):
                        synced_conversations.add(conversation.id)
                        new_messages = sync_result.get('data', {}).get('new_messages_count', 0)
                        new_attachments = sync_result.get('data', {}).get('new_attachments_count', 0)
                        updated_bodies = sync_result.get('data', {}).get('updated_bodies_count', 0)
                        
                        logger.info(f"[GMAIL_WEBHOOK] Conversation {conversation.id} has {new_messages} new messages, {new_attachments} attachments, {updated_bodies} bodies updated")
                        
                        # Store conversation details (include all synced conversations, even with 0 new messages)
                        conversations_details.append({
                            "conversation_id": conversation.id,
                            "conversation_code": conversation.code,
                            "gmail_thread_id": conversation.gmail_thread_id,
                            "insurer_id": conversation.insurer.id if conversation.insurer else None,
                            "insurer_name": conversation.insurer.name if conversation.insurer else None,
                            "new_messages_count": new_messages,
                            "new_attachments_count": new_attachments,
                            "updated_bodies_count": updated_bodies
                        })
                        
                        # Check if any new messages are from insurers and send notifications
                        if new_messages > 0:
                            notifications_sent += _send_notifications_for_new_insurer_messages(conversation)
                    else:
                        logger.warning(f"[GMAIL_WEBHOOK] Failed to sync conversation {conversation.id}: {sync_result.get('message')}")
                        
                except Exception as conv_error:
                    logger.error(f"[GMAIL_WEBHOOK] Error processing conversation {conversation.id}: {str(conv_error)}")
                    continue
            
            logger.info(f"[GMAIL_WEBHOOK] Processed notification: synced {len(synced_conversations)} conversation(s), sent {notifications_sent} notification(s)")
            
        except Exception as sync_error:
            logger.error(f"[GMAIL_WEBHOOK] Error syncing conversations: {str(sync_error)}")
        
        # Always return 200 to acknowledge receipt (Gmail expects this)
        return Response({
            "status": "acknowledged",
            "type": type_param,
            "id": id_param,
            "type_based_id": type_based_id,
            "synced_conversations": len(synced_conversations),
            "notifications_sent": notifications_sent,
            "conversations": conversations_details
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"[GMAIL_WEBHOOK] Unexpected error: {str(e)}", exc_info=True)
        # Still return 200 to acknowledge (don't want Gmail to retry)
        return Response({"status": "acknowledged", "error": str(e)}, status=status.HTTP_200_OK)


def _send_notifications_for_new_insurer_messages(conversation):
    """
    Check for unread reply messages (from insurer) in a conversation and send a single notification
    with the count, e.g. "You received 2 reply message(s) for this conversation."
    Reply messages are stored in DB with is_seen=False (unread) until the user opens the conversation.
    Returns the number of notifications sent (0 or 1).
    """
    try:
        from envoy.controllers.services.NotificationService import NotificationService

        # Get insurer_id from conversation
        insurer_id = None
        if hasattr(conversation, 'insurer') and conversation.insurer:
            insurer_id = conversation.insurer.id
        elif hasattr(conversation, 'insurer_id'):
            insurer_id = conversation.insurer_id

        # Only process if conversation has insurer_id and type_based_id
        if not insurer_id or not conversation.type_based_id:
            return 0

        # Get insurer email for matching reply messages
        insurer_record = (
            QueryBuilderService("core_service_providers")
            .select("email", "name")
            .where("id", insurer_id)
            .first()
        )

        if not insurer_record or not insurer_record.get("email"):
            return 0

        insurer_email_raw = insurer_record.get("email").strip().lower()

        def normalize_email(email_string):
            if not email_string:
                return ""
            email_string = email_string.strip()
            if "<" in email_string and ">" in email_string:
                start = email_string.find("<") + 1
                end = email_string.find(">")
                if start < end:
                    return email_string[start:end].strip().lower()
            return email_string.lower()

        insurer_email = normalize_email(insurer_email_raw)

        # Count unread reply messages from insurer (stored as is_seen=False)
        unread_reply_count = (
            EmailChatMessage.objects
            .filter(
                conversation=conversation,
                is_seen=False,
            )
            .exclude(from_email__isnull=True)
            .exclude(from_email="")
        )
        # Filter in Python for normalized from_email match (DB may store "Name <email>" or raw email)
        unread_reply_ids = [
            m.id for m in unread_reply_count
            if normalize_email(m.from_email or "") == insurer_email
        ]
        unread_count = len(unread_reply_ids)

        if unread_count == 0:
            return 0

        # Get user_id from conversation
        user_id = None
        if hasattr(conversation, 'user') and conversation.user:
            user_id = conversation.user.id
        if not user_id:
            return 0

        # Extract quotation_request_id from type_based_id for metadata
        type_based_id = conversation.type_based_id
        quotation_request_id = None
        if type_based_id.startswith("QR-"):
            quotation_request_id = type_based_id.replace("QR-", "")
        elif type_based_id.startswith("PR-"):
            quotation_request_id = type_based_id.replace("PR-", "")

        insurer_name = insurer_record.get("name", "Insurer")
        reply_word = "reply" if unread_count == 1 else "replies"
        notification_title = f"New {reply_word.capitalize()} from {insurer_name}"
        notification_message = (
            f"You received {unread_count} reply message{'s' if unread_count != 1 else ''} for this conversation."
        )

        meta_data = {
            "conversation_id": str(conversation.id),
            "conversation_code": conversation.code,
            "insurer_id": str(insurer_id),
            "insurer_name": insurer_name,
            "unread_reply_count": unread_count,
            "message_ids": [str(i) for i in unread_reply_ids],
        }
        if quotation_request_id:
            meta_data["quotation_request_id"] = quotation_request_id

        try:
            NotificationService.generate_notification(
                type_code="email_reply",
                title=notification_title,
                meta_data=meta_data,
                message=notification_message,
                customer_id=None,
                user_id=user_id,
            )
            logger.info(
                f"[NOTIFICATION] Sent notification: {unread_count} unread reply message(s) for conversation {conversation.id} (user: {user_id})"
            )
            return 1
        except Exception as notify_error:
            logger.error(f"[NOTIFICATION] Failed to send notification: {str(notify_error)}")
            return 0

    except Exception as e:
        logger.error(f"[NOTIFICATION] Error checking for insurer notifications: {str(e)}")
        return 0


# ----- Gmail Pub/Sub push webhook (real-time notifications) -----

def _extract_from_and_body_from_gmail_message(message_details: dict) -> tuple:
    """Extract From and body from Gmail API message details. Returns (from_email, body)."""
    import base64
    import re
    headers = message_details.get("payload", {}).get("headers", [])
    from_email = next((h["value"] for h in headers if h.get("name", "").lower() == "from"), "")
    from_email = re.sub(r"[^\x00-\x7F]+", "", from_email)
    body = ""

    def extract_body(payload_obj):
        nonlocal body
        if payload_obj.get("body", {}).get("data"):
            try:
                content = base64.urlsafe_b64decode(payload_obj["body"]["data"]).decode("utf-8", errors="ignore")
                if content.strip():
                    body = content
                    return
            except Exception:
                pass
        if payload_obj.get("parts"):
            for part in payload_obj["parts"]:
                if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                    try:
                        content = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                        if content.strip():
                            body = content
                            return
                    except Exception:
                        pass
                elif part.get("mimeType") == "text/html" and part.get("body", {}).get("data") and not body:
                    try:
                        content = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                        if content.strip():
                            body = content
                            return
                    except Exception:
                        pass
                elif part.get("parts"):
                    extract_body(part)

    extract_body(message_details.get("payload", {}))
    if not body:
        body = message_details.get("snippet", "") or ""
    return (from_email or "(unknown)", body.strip() or "(empty)")


def _extract_full_mail_details(message_details: dict) -> dict:
    """
    Extract full mail details from Gmail API message for logging/printing.
    Returns dict with: message_id, thread_id, from_email, to_email, subject, date, body, snippet.
    """
    import base64
    import re
    payload = message_details.get("payload", {})
    headers = payload.get("headers", [])
    def header(name):
        return next((h.get("value", "") for h in headers if h.get("name", "").lower() == name.lower()), "")

    from_email = re.sub(r"[^\x00-\x7F]+", "", header("From") or "")
    to_email = re.sub(r"[^\x00-\x7F]+", "", header("To") or "")
    subject = re.sub(r"[^\x00-\x7F]+", "", header("Subject") or "").replace("\r", "").replace("\n", " ").strip()
    date_str = header("Date") or ""

    body = ""

    def extract_body(payload_obj):
        nonlocal body
        if payload_obj.get("body", {}).get("data"):
            try:
                content = base64.urlsafe_b64decode(payload_obj["body"]["data"]).decode("utf-8", errors="ignore")
                if content.strip():
                    body = content
                    return
            except Exception:
                pass
        if payload_obj.get("parts"):
            for part in payload_obj["parts"]:
                if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                    try:
                        content = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                        if content.strip():
                            body = content
                            return
                    except Exception:
                        pass
                elif part.get("mimeType") == "text/html" and part.get("body", {}).get("data") and not body:
                    try:
                        content = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                        if content.strip():
                            body = content
                            return
                    except Exception:
                        pass
                elif part.get("parts"):
                    extract_body(part)

    extract_body(payload)
    if not body:
        body = message_details.get("snippet", "") or ""

    return {
        "message_id": message_details.get("id", ""),
        "thread_id": message_details.get("threadId", ""),
        "from_email": from_email or "(unknown)",
        "to_email": to_email or "(unknown)",
        "subject": subject or "(no subject)",
        "date": date_str or "(no date)",
        "body": (body or "").strip() or "(empty)",
        "snippet": (message_details.get("snippet") or "").strip(),
    }


def _print_new_message_from_gmail(cred, message_id: str, inbox_email: str = "") -> None:
    """
    When a new mail is received (push triggered), fetch that message and print its exact details:
    message_id, thread_id, From, To, Subject, Date, Body. Also logs the same to application log.
    """
    import envoy.services.email_service as svc
    try:
        message_details = svc.get_message_details(cred, message_id)
        details = _extract_full_mail_details(message_details)
        to_inbox = inbox_email or (cred.system_email if cred else "")

        # Log so it appears in application logs
        logger.info(
            "[GMAIL_PUBSUB] New mail received | message_id=%s | thread_id=%s | from=%s | to=%s | subject=%s",
            details["message_id"],
            details["thread_id"],
            details["from_email"],
            details["to_email"],
            details["subject"],
        )

        # Print exact mail details to console (same as thread)
        print("\n" + "=" * 60)
        print("[GMAIL_PUBSUB] NEW MAIL RECEIVED (from this thread)")
        print("=" * 60)
        print(f"  Message ID : {details['message_id']}")
        print(f"  Thread ID : {details['thread_id']}")
        print(f"  To (inbox): {to_inbox}")
        print(f"  From      : {details['from_email']}")
        print(f"  To        : {details['to_email']}")
        print(f"  Subject   : {details['subject']}")
        print(f"  Date      : {details['date']}")
        print("  --- Body ---")
        print(details["body"])
        print("  ---")
        print("=" * 60 + "\n")
    except Exception as e:
        logger.warning(f"[GMAIL_PUBSUB] Could not fetch/print message {message_id}: {e}")
        print(f"[GMAIL_PUBSUB] Could not fetch/print message {message_id}: {e}")


def _handle_gmail_history(history_id: str, email_address: str) -> None:
    """
    Fetch Gmail history and sync affected threads to ChatConversation.
    Push sends the *current* historyId (after the change); we must request history *after* the
    previous id, so we use startHistoryId = (push historyId - 1) to get the new message(s).
    Prints From + full body for every new message, then runs sync for linked conversations.
    """
    import envoy.services.email_service as svc
    try:
        cred = GmailCredential.objects.filter(system_email=email_address).first()
        if not cred:
            logger.warning(f"[GMAIL_PUBSUB] No Gmail credential for {email_address}")
            return
        cred = ensure_fresh_token(cred)

        # Determine startHistoryId:
        # - Prefer last_history_id we have already processed (gap-safe)
        # - Fallback to (push historyId - 1) heuristic on first run
        stored_last = getattr(cred, "last_history_id", None)
        if stored_last:
            start_history_id = str(stored_last)
        else:
            try:
                start_history_id = str(max(1, int(history_id) - 1))
            except (TypeError, ValueError):
                start_history_id = history_id

        seen_thread_ids = set()
        page_token = None
        total_printed = 0
        while True:
            history_response = svc.get_history(cred, start_history_id, max_results=100, page_token=page_token)
            history_items = history_response.get("history", [])
            for item in history_items:
                messages_added = item.get("messagesAdded", [])
                for msg_added in messages_added:
                    msg = msg_added.get("message") if isinstance(msg_added.get("message"), dict) else {}
                    if not msg and isinstance(msg_added, dict) and "id" in msg_added:
                        msg = msg_added
                    message_id = msg.get("id") if isinstance(msg, dict) else None
                    thread_id = msg.get("threadId") if isinstance(msg, dict) else None
                    if message_id:
                        _print_new_message_from_gmail(cred, str(message_id), email_address)
                        total_printed += 1
                    if thread_id and thread_id not in seen_thread_ids:
                        seen_thread_ids.add(thread_id)
                        _process_new_message(thread_id)
            page_token = history_response.get("nextPageToken")
            if not page_token:
                break

        # Update last_history_id so the next push starts from here and avoids gaps
        try:
            cred.last_history_id = str(history_id)
            cred.save(update_fields=["last_history_id"])
        except Exception as save_err:
            logger.warning(
                "[GMAIL_PUBSUB] Could not persist last_history_id=%s for %s: %s",
                history_id,
                email_address,
                save_err,
            )
        if total_printed == 0:
            if not history_response.get("history"):
                logger.debug("[GMAIL_PUBSUB] No history records for startHistoryId=%s (push historyId=%s)", start_history_id, history_id)
            else:
                logger.debug("[GMAIL_PUBSUB] History had items but no messagesAdded with message id")
    except Exception as e:
        logger.error(f"[GMAIL_PUBSUB] Error in _handle_gmail_history: {str(e)}", exc_info=True)
        print(f"[GMAIL_PUBSUB] Error: {e}")


def _broadcast_new_mail_to_stream(conversation) -> None:
    """
    Notify the conversation owner via SSE so /api/notifications/stream receives a new_notification event.
    Called when new mail is synced for this conversation so the frontend can refetch notifications/chatmail.
    """
    try:
        user_id = getattr(conversation, "user_id", None) or (
            conversation.user.id if getattr(conversation, "user", None) else None
        )
        if user_id:
            from envoy.controllers.notification_live import broadcast_new_notification
            broadcast_new_notification(user_id)
            logger.debug("[GMAIL_PUBSUB] Broadcast new_notification to stream for user_id=%s (conversation %s)", user_id, conversation.id)
    except Exception as e:
        logger.warning("[GMAIL_PUBSUB] Failed to broadcast new mail to stream: %s", e)


def _process_new_message(thread_id: str) -> None:
    """
    Map thread_id to ChatConversation and run sync_gmail_thread_messages; notify if new messages.
    When new messages are synced, push to SSE stream so connected clients get real-time update.
    """
    try:
        conversation = ChatConversation.objects.filter(gmail_thread_id=thread_id).first()
        if not conversation:
            return
        result = sync_gmail_thread_messages(conversation.id)
        if not result.get("success"):
            return
        new_count = result.get("data", {}).get("new_messages_count", 0)
        if new_count > 0:
            _send_notifications_for_new_insurer_messages(conversation)
            # Push to notification stream so SSE clients get real-time update (even if no
            # email_reply notification was created, e.g. sender not insurer)
            _broadcast_new_mail_to_stream(conversation)
    except Exception as e:
        logger.error(f"[GMAIL_PUBSUB] Error in _process_new_message thread {thread_id}: {str(e)}", exc_info=True)


def _run_gmail_history_sync(history_id: str, email_address: str | None) -> None:
    """Run history sync in background; used by gmail_webhook to avoid proxy timeouts (502)."""
    try:
        mailbox = email_address
        if not mailbox:
            cred = GmailCredential.objects.first()
            mailbox = cred.system_email if cred else "(first credential)"
        print(f"[GMAIL_PUBSUB] Processing history sync for inbox: {mailbox} | historyId: {history_id}")
        if email_address:
            _handle_gmail_history(history_id, email_address)
        else:
            if cred:
                _handle_gmail_history(history_id, cred.system_email)
    except Exception as e:
        logger.error(f"[GMAIL_PUBSUB] Background sync error: {str(e)}", exc_info=True)
    finally:
        from django.db import connection
        connection.close()


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def gmail_webhook(request):
    """
    Pub/Sub push endpoint for Gmail push notifications.
    Expects POST body: { "message": { "data": "<base64-encoded JSON>" } }
    Decoded data: { "emailAddress": "...", "historyId": "..." }
    Returns 200 immediately and processes sync in a background thread to avoid 502 timeouts.
    """
    import base64
    import json
    import threading
    try:
        data = getattr(request, "data", None) or (json.loads(request.body.decode("utf-8")) if request.body else {})
        message = data.get("message")
        if not message:
            return Response({"status": "no message"}, status=status.HTTP_200_OK)
        raw_data = message.get("data")
        if not raw_data:
            return Response({"status": "no data"}, status=status.HTTP_200_OK)
        decoded = base64.b64decode(raw_data).decode("utf-8")
        payload = json.loads(decoded)
        email_address = payload.get("emailAddress")
        history_id = "".join(str(payload.get("historyId") or "").split())
        if not history_id:
            return Response({"status": "missing historyId"}, status=status.HTTP_200_OK)
        # If GMAIL_WATCH_ONLY_EMAIL is set, only process pushes for that mailbox (e.g. envoy.cloud.services@gmail.com)
        watch_only = os.getenv("GMAIL_WATCH_ONLY_EMAIL", "").strip()
        if watch_only and (not email_address or str(email_address or "").strip().lower() != watch_only.lower()):
            print(f"[GMAIL_PUBSUB] Skipped (only watching {watch_only}): inbox={email_address or '(none)'}")
            return Response({"status": "skipped", "reason": "only_this_inbox"}, status=status.HTTP_200_OK)
        inbox_display = "".join(str(email_address or "(from payload)").split()).replace("\n", " ").replace("\r", " ")
        print(f"[GMAIL_PUBSUB] Webhook triggered | Inbox (TO): {inbox_display} | historyId: {history_id}")
        # Process in background so we return 200 quickly and avoid proxy timeout (502)
        thread = threading.Thread(
            target=_run_gmail_history_sync,
            args=(history_id, email_address),
            daemon=True,
        )
        thread.start()
        return Response({"status": "received"}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"[GMAIL_PUBSUB] Webhook error: {str(e)}", exc_info=True)
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_200_OK)