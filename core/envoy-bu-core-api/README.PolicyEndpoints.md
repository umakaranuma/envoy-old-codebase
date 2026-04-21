# Policy API Endpoints Documentation

## Overview
This document describes the policy-specific chat endpoints for managing email conversations related to policies, similar to the quotation endpoints but for policy entities.

## Endpoints

### 1. 💬 **Get Policy Chat Messages**
**GET** `/api/<policy_id>/chat-messages`

**Purpose**: Get chat messages for a specific policy by finding the conversation and fetching messages

**Path Parameters**:
- `policy_id` (required): ID of the policy

**Query Parameters** (forwarded to chatmail messages endpoint):
- `sync_thread` (optional): Set to 'true' to sync with Gmail (default: 'false')
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 10)
- `user_id` (optional): Filter by user ID

**How it works**:
1. Finds the conversation in `core_chat_conversations` table where:
   - `type_based_id` = `PR-{policy_id}`
2. Gets the `conversation_id` from that record
3. Calls the existing `/api/chatmail/messages` endpoint with the found `conversation_id`

**Examples**:
```bash
# Get messages for policy 123
GET /api/123/chat-messages

# With Gmail sync
GET /api/123/chat-messages?sync_thread=true

# With pagination
GET /api/123/chat-messages?page=2&page_size=20
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
        "gmail_message_id": "msg_123",
        "from_email": "sender@example.com",
        "to_email": "recipient@example.com",
        "subject": "Re: Policy Update",
        "body": "Thank you for your inquiry...",
        "sent_at": "2025-08-16T19:11:57Z",
        "type": "received",
        "sender_name": "John Doe",
        "attachments": [
          {
            "id": 3,
            "file_name": "policy_document.pdf",
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
    },
    "conversation_metadata": {
      "conversation_id": 1,
      "conversation_code": "ADC69ECA92",
      "type": "POLICY",
      "created_at": "2025-08-16T19:11:57Z",
             "policy_id": 123,
       "type_based_id": "PR-123"
    }
  }
}
```

**Error Responses**:
```json
{
  "is_success": false,
  "message": "No conversation found for policy 123",
  "result": null,
  "system_code": "NOT_FOUND"
}
```

---

### 2. 🔄 **Policy Sync Conversations**
**POST** `/api/<policy_id>/sync-conversations`

**Purpose**: Sync all conversations for a specific policy with Gmail

**Path Parameters**:
- `policy_id` (int): The policy ID

**How it works**:
1. Finds all conversations in `core_chat_conversations` where `type_based_id = 'PR-{policy_id}'`
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
    "policy_id": 123,
    "type_based_id": "PR-123",
    "total_conversations": 3,
    "successful_syncs": 2,
    "failed_syncs": 1,
    "sync_results": [
      {
        "conversation_id": "conv_123",
        "insurer_id": "456",
        "status": "success",
        "response": {
          "success": true,
          "data": {
            "new_messages": 2,
            "updated_messages": 1,
            "sync_time": "2025-08-16T19:20:45Z"
          }
        },
        "conversation_code": "CONV-001",
        "type": "POLICY"
      },
      {
        "conversation_id": "conv_124",
        "insurer_id": "457",
        "status": "success",
        "response": {
          "success": true,
          "data": {
            "new_messages": 0,
            "updated_messages": 0,
            "sync_time": "2025-08-16T19:20:45Z"
          }
        },
        "conversation_code": "CONV-002",
        "type": "POLICY"
      },
      {
        "conversation_id": "conv_125",
        "insurer_id": "458",
        "status": "failed",
        "error": "HTTP 404: Conversation not found",
        "conversation_code": "CONV-003",
        "type": "POLICY"
      }
    ]
  },
  "message": "Partially synced conversations for policy 123: 2 successful, 1 failed"
}
```

**Status Codes**:
- `SUCCESS`: All conversations synced successfully
- `PARTIAL_SUCCESS`: Some conversations synced successfully, some failed
- `PARTIAL_FAILURE`: All conversations failed to sync
- `NOT_FOUND`: No conversations found for the policy

---

## Usage Scenarios

### **Scenario 1: Quick Policy Message View**
```bash
# Fast database-only fetch
GET /api/123/chat-messages
```

### **Scenario 2: Check for New Policy Replies**
```bash
# Sync with Gmail and get latest messages
GET /api/123/chat-messages?sync_thread=true
```

### **Scenario 3: Sync All Policy Conversations**
```bash
# Sync all conversations for a policy
POST /api/123/sync-conversations
```

### **Scenario 4: Get Policy Messages with Pagination**
```bash
# Get messages with pagination
GET /api/123/chat-messages?page=2&page_size=20
```

---

## Database Schema

### Core Tables:
- `core_chat_conversations`: Stores conversation metadata
- `core_email_messages`: Stores individual email messages
- `core_email_attachments`: Stores email attachments

### Key Fields for Policies:
- `type_based_id`: Format "PR-{policy_id}" for policies
- `insurer_id`: Links to service provider/insurer
- `conversation_id`: Links messages to conversations
- `gmail_message_id`: External Gmail message ID for sync

---

## Differences from Quotation Endpoints

| Feature | Quotation Endpoints | Policy Endpoints |
|---------|-------------------|------------------|
| URL Pattern | `/api/<quotation_id>/chat-messages/<insurer_id>` | `/api/<policy_id>/chat-messages` |
| Type Based ID | `QR-{quotation_id}` | `PR-{policy_id}` |
| Conversation Type | `QUOTATION` | `POLICY` |
| Entity Type | Quotation | Policy |

---

## Testing

Use the provided test script `test_policy_endpoints.py` to test the endpoints:

```bash
# Set your auth token
export AUTH_TOKEN="your_token_here"

# Run the test script
python test_policy_endpoints.py
```

The test script will:
1. Test getting policy chat messages (database only)
2. Test getting policy chat messages with Gmail sync
3. Test syncing all conversations for a policy

---

## Error Handling

### Common Error Scenarios:

1. **No Conversation Found**
   - Occurs when no conversation exists for the given policy_id
   - Returns `NOT_FOUND` status

2. **Authentication Required**
   - Occurs when no valid auth token is provided
   - Returns `UNAUTHORIZED` status

3. **Sync Failures**
   - Occurs when Gmail sync operations fail
   - Returns detailed error information in sync results

4. **Invalid Parameters**
   - Occurs when policy_id is invalid
   - Returns appropriate validation error

---

## Integration Notes

- These endpoints follow the same pattern as quotation endpoints
- They use the same underlying chatmail infrastructure
- Authentication and authorization follow the same rules
- Error handling and response formats are consistent
- The endpoints are designed to work with existing Gmail integration
