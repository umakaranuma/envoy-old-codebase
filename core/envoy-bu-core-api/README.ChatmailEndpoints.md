# Chatmail API Endpoints Documentation

## Overview
This document describes all the chatmail endpoints for managing email conversations, syncing with Gmail, and handling attachments.

## Endpoints

### 1. 📥 **Fetch Messages (Database + Optional Gmail Sync)**
**GET** `/api/chatmail/messages`

**Purpose**: Retrieve messages from database with optional Gmail sync

**Query Parameters**:
- `conversation_id` (required): ID of the conversation
- `user_id` (optional): Filter by user ID
- `sync_thread` (optional): Set to 'true' to sync with Gmail (default: 'false')
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 10)

**Response Time**: 
- Database only: < 100ms
- With Gmail sync: 6-8 seconds (includes body updates for existing messages)

**Examples**:
```bash
# Fast database-only fetch
GET /api/chatmail/messages?conversation_id=1

# With Gmail sync (slower but gets latest replies)
GET /api/chatmail/messages?conversation_id=1&sync_thread=true
```

**Response**:
```json
{
  "success": true,
  "message": "Messages retrieved successfully from database",
  "data": {
    "messages": [
      {
        "id": 1,
        "conversation_id": 1,
        "conversation_code": "ADC69ECA92",
        "from_email": "sender@example.com",
        "to_email": "recipient@example.com",
        "subject": "Re: New Request",
        "body": "Thank you for your inquiry...",
        "sent_at": "2025-08-16T19:11:57Z",
        "gmail_message_id": "msg_123",
        "attachments": [
          {
            "id": 3,
            "file_name": "document.pdf",
            "content_type": "application/pdf",
            "size_bytes": 1024000,
            "is_image": false,
            "file_url": "gmail://attachment/msg_123/att_456",
            "download_url": "/api/chatmail/download-attachment?attachment_id=3"
          }
        ]
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 10,
      "total_count": 25,
      "total_pages": 3
    }
  }
}
```

---

### 2. 📤 **Send Message**
**POST** `/api/chatmail/send`

**Purpose**: Send a new email message and store it in the database

**Request Body**:
```json
{
  "to_email": "recipient@example.com",
  "from_email": "sender@example.com",
  "subject": "New Request",
  "body": "Hello, I have a new request...",
  "conversation_id": "1",
  "conversation_type": "QUOTATION",
  "type_based_id": "QR-123",
  "insurer_id": 456
}
```

**Response**:
```json
{
  "success": true,
  "message": "Message sent successfully",
  "data": {
    "message_id": 7,
    "conversation_id": 1,
    "gmail_message_id": "msg_789",
    "sent_at": "2025-08-16T19:15:30Z"
  }
}
```

---

### 3. 🔄 **Sync Gmail Thread**
**POST** `/api/chatmail/sync-thread`

**Purpose**: Manually sync a conversation with Gmail to get latest messages

**Request Body**:
```json
{
  "conversation_id": 1
}
```

**Response**:
```json
{
  "success": true,
  "message": "Thread synced successfully",
  "data": {
    "new_messages": 3,
    "updated_messages": 1,
    "sync_time": "2025-08-16T19:20:45Z"
  }
}
```

---

### 4. 📎 **Download Attachment**
**GET** `/api/chatmail/download-attachment`

**Purpose**: Download an email attachment

**Query Parameters**:
- `attachment_id` (required): ID of the attachment

**Response**: File download with appropriate headers

---

### 5. 📋 **Get Attachment Info**
**GET** `/api/chatmail/attachment-info`

**Purpose**: Get attachment metadata without downloading

**Query Parameters**:
- `attachment_id` (required): ID of the attachment

**Response**:
```json
{
  "success": true,
  "message": "Attachment information retrieved successfully",
  "data": {
    "id": 3,
    "file_name": "document.pdf",
    "content_type": "application/pdf",
    "size_bytes": 1024000,
    "is_image": false,
    "created_at": "2025-08-16T19:11:57Z",
    "download_url": "/api/chatmail/download-attachment?attachment_id=3",
    "message_info": {
      "message_id": 7,
      "subject": "Re: New Request",
      "conversation_id": 1,
      "conversation_code": "ADC69ECA92"
    }
  }
}
```

---

### 6. 📋 **Get Conversations**
**GET** `/api/chatmail/conversations`

**Purpose**: List all chatmail conversations

**Query Parameters**:
- `user_id` (optional): Filter by user ID
- `conversation_type` (optional): Filter by type (POLICY, QUOTATION, ENDORSEMENT)
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 10)

**Response**:
```json
{
  "success": true,
  "message": "Conversations retrieved successfully",
  "data": {
    "conversations": [
      {
        "id": 1,
        "code": "ADC69ECA92",
        "type": "QUOTATION",
        "type_based_id": "123",
        "insurer_id": 456,
        "insurer_name": "ABC Insurance",
        "user_id": 1,
        "user_name": "John Doe",
        "gmail_thread_id": "thread_123",
        "created_at": "2025-08-16T19:11:57Z",
        "message_count": 5
      }
    ],
    "pagination": {...}
  }
}
```

---

### 7. 💬 **Get Quotation Chat Messages**
**GET** `/api/<quotation_id>/chat-messages/<insurer_id>`

**Purpose**: Get chat messages for a specific quotation and insurer by finding the conversation and fetching messages

**Path Parameters**:
- `quotation_id` (required): ID of the quotation
- `insurer_id` (required): ID of the insurer

**Query Parameters** (forwarded to chatmail messages endpoint):
- `sync_thread` (optional): Set to 'true' to sync with Gmail (default: 'false')
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 10)
- `user_id` (optional): Filter by user ID

**How it works**:
1. Finds the conversation in `core_chat_conversations` table where:
   - `type_based_id` = `QR-{quotation_id}`
   - `insurer_id` = `{insurer_id}`
2. Gets the `conversation_id` from that record
3. Calls the existing `/api/chatmail/messages` endpoint with the found `conversation_id`

**Examples**:
```bash
# Get messages for quotation 123 and insurer 456
GET /api/123/chat-messages/456

# With Gmail sync
GET /api/123/chat-messages/456?sync_thread=true

# With pagination
GET /api/123/chat-messages/456?page=2&page_size=20
```

**Response**:
```json
{
  "success": true,
  "message": "Messages retrieved successfully from database",
  "data": {
    "messages": [...],
    "pagination": {...},
    "conversation_metadata": {
      "conversation_id": 1,
      "conversation_code": "ADC69ECA92",
      "type": "QUOTATION",
      "created_at": "2025-08-16T19:11:57Z",
      "quotation_id": 123,
      "insurer_id": 456,
      "type_based_id": "QR-123"
    }
  }
}
```

**Error Responses**:
```json
{
  "is_success": false,
  "message": "No conversation found for quotation 123 and insurer 456",
  "result": null,
  "system_code": "NOT_FOUND"
}
```

---

## Usage Scenarios

### **Scenario 1: Quick Message View**
```bash
# Fast database-only fetch
GET /api/chatmail/messages?conversation_id=1
```

### **Scenario 2: Check for New Replies**
```bash
# Sync with Gmail and get latest messages
GET /api/chatmail/messages?conversation_id=1&sync_thread=true
```

### **Scenario 3: Send New Message**
```bash
# Send and store new message
POST /api/chatmail/send
{
  "to_email": "client@example.com",
  "from_email": "agent@company.com",
  "subject": "Re: Insurance Quote",
  "body": "Thank you for your inquiry...",
  "conversation_id": "1",
  "conversation_type": "QUOTATION",
  "type_based_id": "QR-123",
  "insurer_id": 456
}
```

### **Scenario 4: Get Quotation Messages**
```bash
# Get all messages for a specific quotation and insurer
GET /api/123/chat-messages/456

# With Gmail sync to get latest replies
GET /api/123/chat-messages/456?sync_thread=true
```

---

## Database Schema

### Core Tables:
- `core_chat_conversations`: Stores conversation metadata
- `core_emailchatmessage`: Stores individual email messages
- `core_emailattachment`: Stores email attachments

### Key Fields:
- `type_based_id`: Format varies by type (e.g., "QR-123" for quotations)
- `insurer_id`: Links to service provider/insurer
- `conversation_id`: Links messages to conversations
- `gmail_message_id`: External Gmail message ID for sync

---

### 7. 🔄 **Quotation Sync Conversations**
**POST** `/api/<quotation_id>/sync-conversations`

**Purpose**: Sync all conversations for a specific quotation with Gmail

**Path Parameters**:
- `quotation_id` (int): The quotation ID

**How it works**:
1. Finds all conversations in `core_chat_conversations` where `type_based_id = 'QR-{quotation_id}'`
2. For each conversation found, calls the `/api/chatmail/sync-thread` endpoint
3. Returns detailed results for each sync operation

**Response**: Summary of sync operations with individual results

**Example**:
```bash
POST /api/123/sync-conversations
```

**Response Example**:
```json
{
  "success": true,
  "data": {
    "quotation_id": 123,
    "type_based_id": "QR-123",
    "total_conversations": 3,
    "successful_syncs": 2,
    "failed_syncs": 1,
    "sync_results": [
      {
        "conversation_id": "conv_123",
        "insurer_id": "456",
        "status": "success",
        "response": {...},
        "conversation_code": "CONV-001",
        "type": "QUOTATION"
      },
      {
        "conversation_id": "conv_124",
        "insurer_id": "457",
        "status": "success",
        "response": {...},
        "conversation_code": "CONV-002",
        "type": "QUOTATION"
      },
      {
        "conversation_id": "conv_125",
        "insurer_id": "458",
        "status": "failed",
        "error": "HTTP 404: Conversation not found",
        "conversation_code": "CONV-003",
        "type": "QUOTATION"
      }
    ]
  },
  "message": "Partially synced conversations for quotation 123: 2 successful, 1 failed"
}
```

**Status Codes**:
- `SUCCESS`: All conversations synced successfully
- `PARTIAL_SUCCESS`: Some conversations synced successfully, some failed
- `PARTIAL_FAILURE`: All conversations failed to sync
- `NOT_FOUND`: No conversations found for the quotation
