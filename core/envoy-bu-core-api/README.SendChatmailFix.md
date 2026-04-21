# Send Chatmail Message Endpoint Fix

## 🐛 **Issue Description**

When using the `POST /api/chatmail/send` endpoint with a `conversation_id`, the system was incorrectly deriving the `to_email` from the latest email in the conversation instead of from the insurer associated with that conversation.

### **Problem Scenario**
```json
{
    "body": "sending through the mail postman",
    "conversation_id": 4
}
```

**Expected Behavior**: Email should be sent from the system email to the insurer's email
**Actual Behavior**: Email was being sent from the system email to the same email (system email)

## 🔧 **Root Cause**

The issue was in the email derivation logic in `envoy/controllers/chatmail_controller.py`. When a `conversation_id` was provided, the system was:

1. Looking up the latest email in the conversation
2. Using that email's `to_email` as the recipient
3. This caused the system to send emails to itself instead of to the insurer

## ✅ **Fix Applied**

The fix updates the email derivation logic to:

1. **First Priority**: Get the `to_email` from the conversation's associated insurer
2. **Fallback**: Only if no insurer is found, derive from the latest email in the conversation
3. **Proper Error Handling**: Added proper exception handling for missing conversations

### **Updated Logic Flow**

```python
# If conversation_id is provided, try to derive addresses when missing
if conversation_id:
    # 1. Get the conversation and derive to_email from insurer
    conversation = ChatConversation.objects.get(id=conversation_id)
    if not to_email and conversation.insurer_id:
        insurer_record = QueryBuilderService("core_service_providers")
            .select("email")
            .where("id", conversation.insurer_id)
            .first()
        if insurer_record and insurer_record.get("email"):
            to_email = insurer_record["email"].strip()
    
    # 2. Fallback: derive to_email from latest email if no insurer found
    if not to_email:
        latest_email = EmailChatMessage.objects
            .filter(conversation_id=conversation_id)
            .order_by("-sent_at", "-id")
            .first()
        if latest_email:
            to_email = latest_email.to_email
    
    # 3. For from_email: ALWAYS prefer system email from Gmail credentials
    if not from_email:
        gmail_credential_row = QueryBuilderService("core_gmailcredential")
            .select("system_email")
            .orderBy("id", "asc")
            .first()
        if gmail_credential_row and gmail_credential_row.get("system_email"):
            from_email = gmail_credential_row["system_email"]
        else:
            # Only fallback to latest email's from_email if no system email found
            latest_email = EmailChatMessage.objects
                .filter(conversation_id=conversation_id)
                .order_by("-sent_at", "-id")
                .first()
            if latest_email:
                from_email = latest_email.from_email
```

## 📧 **How to Send Attachments**

### **Attachment Format**
```json
{
    "body": "Please find the attached documents",
    "conversation_id": 4,
    "attachments": [
        {
            "file_name": "document.pdf",
            "file_url": "https://example.com/files/document.pdf",
            "content_type": "application/pdf",
            "size_bytes": 1024000,
            "is_image": false,
            "gmail_attachment_id": "optional_gmail_id"
        },
        {
            "file_name": "image.jpg",
            "file_url": "https://example.com/files/image.jpg",
            "content_type": "image/jpeg",
            "size_bytes": 512000,
            "is_image": true
        }
    ]
}
```

### **Required Attachment Fields**
- `file_name`: Name of the file (e.g., "document.pdf")
- `file_url`: URL where the file can be accessed
- `content_type`: MIME type of the file (e.g., "application/pdf")
- `size_bytes`: File size in bytes

### **Optional Attachment Fields**
- `is_image`: Boolean indicating if the file is an image (default: false)
- `gmail_attachment_id`: Gmail attachment ID if this is a reply to a Gmail message

## 🧪 **Testing the Fix**

Use the provided test script to verify the fix:

```bash
python test_send_chatmail_fix.py
```

### **Test Cases**
1. **Simple Message**: Send a basic message with conversation_id
2. **Custom Subject**: Send message with custom subject
3. **With Attachments**: Send message with file attachments

## 📋 **API Usage Examples**

### **Example 1: Simple Message**
```bash
POST /api/chatmail/send
Content-Type: application/json
Authorization: Bearer <your_token>

{
    "body": "Hello, this is a test message",
    "conversation_id": 4
}
```

### **Example 2: Message with Attachments**
```bash
POST /api/chatmail/send
Content-Type: application/json
Authorization: Bearer <your_token>

{
    "body": "Please find the attached quotation documents",
    "conversation_id": 4,
    "attachments": [
        {
            "file_name": "quotation.pdf",
            "file_url": "https://storage.example.com/quotation.pdf",
            "content_type": "application/pdf",
            "size_bytes": 2048000,
            "is_image": false
        }
    ]
}
```

### **Example 3: New Conversation**
```bash
POST /api/chatmail/send
Content-Type: application/json
Authorization: Bearer <your_token>

{
    "to_email": "insurer@example.com",
    "subject": "New Quotation Request",
    "body": "Please review the attached quotation",
    "conversation_type": "QUOTATION",
    "type_based_id": "QR-123",
    "insurer_id": 456
}
```

## 🔍 **Verification**

After the fix, when you send a message with `conversation_id: 4`:

### **For `to_email` (Recipient)**:
1. **System will**: Look up conversation ID 4
2. **Find insurer**: Get the insurer_id from the conversation
3. **Get email**: Query the insurer's email from `core_service_providers`
4. **Fallback**: If no insurer found, use latest email's to_email

### **For `from_email` (Sender)**:
1. **Priority**: Always use system email from `core_gmailcredential` table
2. **Fallback**: Only if no system email found, use latest email's from_email
3. **Result**: Email sent FROM system email TO insurer email (correctly)

## 📝 **Logging**

The fix includes enhanced logging to help debug email derivation:

```
[DEBUG] Looking for conversation_id: 4
[send_chatmail_message] Derived to_email 'insurer@example.com' from conversation insurer_id 456
[DEBUG] After normalization:
[DEBUG] to_email: 'insurer@example.com'
[DEBUG] from_email: 'system@company.com'
```

## 🚀 **Deployment**

The fix is backward compatible and doesn't require any database changes. Simply deploy the updated `chatmail_controller.py` file.
