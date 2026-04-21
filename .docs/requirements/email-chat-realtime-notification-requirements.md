# Email Chat Real-Time Notification & Reply Display — Requirements

## 1. Overview

This feature ensures that when the system receives an email reply (from an insurer), the reply is immediately fetched from Gmail, stored in the database, shown as a **real-time notification** to the relevant user, and the reply content is displayed inside the **endorsement chat panel** (in the Policy module's Issued Policy → Endorsement Request single view).

The same pattern already exists for **Quotation Chat** in the CRM module's quotation view (sending emails to service providers, syncing reply threads, and displaying them in a chat-like UI). This requirement extends and solidifies that pattern for endorsement requests within the Policy module, ensuring real-time delivery.

---

## 2. Current System Architecture

### 2.1 Modules Involved

| Module | Role |
|--------|------|
| **Core API** (`envoy_core/envoy_core_api`) | Gmail integration, Chatmail send/sync, Notifications (SSE + polling), Gmail Pub/Sub webhook |
| **Core UI** (`envoy_core/envoy_core_ui`) | Notification Provider context, Notification page, Header notification bell |
| **CRM UI** (`envoy_crm/envoy_crm_ui`) | Quotation chat (same `Chat.tsx` component pattern) — reference implementation |
| **Policy API** (`envoy_policy/envoy_policy_api`) | Endorsement request CRUD, send endorsement email, sync conversations via Core API |
| **Policy UI** (`envoy_policy/envoy_policy_ui`) | Endorsement request list, chat panel (ChatContent.tsx using shared Chat.tsx) |

### 2.2 Existing Data Flow

```
┌─────────────────────────────┐
│  User sends endorsement     │
│  email from Policy UI       │
├─────────────────────────────┤
│  Policy API calls           │
│  Core /api/chatmail/send    │
│  → Gmail API → Email sent   │
│  → ChatConversation created │
│  → EmailChatMessage stored  │
└──────────┬──────────────────┘
           │
           ▼ (Insurer replies externally)
┌─────────────────────────────┐
│  Gmail Pub/Sub Webhook      │
│  → POST /api/gmail/push-webhook │
│  → _handle_gmail_history()  │
│  → sync_gmail_thread_messages()│
│  → New EmailChatMessage(is_seen=false)│
│  → _send_notifications_...  │
│  → NotificationService.generate_notification()│
│  → broadcast_new_notification (SSE)│
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│  Frontend detects:          │
│  • SSE event (stream) OR    │
│  • Polling /notifications-  │
│    unread-count             │
│  → Refreshes notification   │
│    panel                    │
│  → User clicks → navigates  │
│    to chat                  │
└─────────────────────────────┘
```

### 2.3 Existing Database Tables

| Table | Purpose |
|-------|---------|
| `core_chat_conversations` | Stores conversation metadata: type (QUOTATION/ENDORSEMENT/POLICY), type_based_id (QR-{id}/ER-{id}), insurer_id, gmail_thread_id |
| `core_emailchatmessage` | Individual email messages: from/to, subject, body, sent_at, is_seen, conversation FK |
| `core_emailattachment` | Attachments linked to email messages |
| `core_gmailcredential` | Gmail OAuth tokens and system_email |
| `core_notifications` | Notification records: title, message, metadata (JSON), type_id |
| `core_notification_users` | User-to-notification link: is_read, read_at |
| `core_notification_types` | Notification type codes (e.g. `email_reply`) |

### 2.4 Existing API Endpoints (Core API)

| Endpoint | Purpose |
|----------|---------|
| `POST /api/chatmail/send` | Send email via Gmail, create/update conversation |
| `GET /api/chatmail/messages?conversation_id=X` | Fetch messages from DB (optional `sync_thread=true`) |
| `POST /api/chatmail/sync-thread` | Sync a conversation with Gmail |
| `GET /api/chatmail/conversations` | List all chatmail conversations |
| `POST /api/chatmail/mark-conversation-seen` | Mark conversation as seen |
| `GET /api/chatmail/download-attachment?attachment_id=X` | Download attachment |
| `POST /api/gmail/push-webhook` | Gmail Pub/Sub (real-time incoming mail) |
| `POST /api/chatmail/gmail-webhook` | Manual webhook trigger with type/id/mail |
| `GET /api/policy/{policy_id}/sync-endorsement-requests` | Sync all endorsement conversations for a policy |
| `GET /api/all-notifications` | List notifications (paginated, filterable) |
| `GET /api/notifications-unread-count` | Unread count for polling/badge |
| `GET /api/notifications/stream?token=X` | SSE stream for real-time push |
| `POST /api/read-notifications/{ids}` | Mark notifications as read |

### 2.5 Existing UI Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `Chat.tsx` | `policy-ui/src/components/others/page-related/chat/Chat.tsx` | Shared chat component (messages list, send input, compose modal) |
| `ChatContent.tsx` | `policy-ui/.../endorsement-requests/ChatContent.tsx` | Wrapper passing endorsement-specific props to `Chat.tsx` |
| `CreateMsg.tsx` | `policy-ui/.../chat/_utils/components/CreateMsg.tsx` | Compose new email message |
| `ViewMsg.tsx` | `policy-ui/.../chat/_utils/components/ViewMsg.tsx` | View single message with attachments |
| `NotificationProvider.tsx` | `core-ui/src/contexts/NotificationProvider.tsx` | React context for notifications (reloadNotification) |
| `Notifications.tsx` | `core-ui/src/app/a/notifications/...` | Notification list page |

---

## 3. Requirements

### 3.1 Real-Time Email Fetch on Incoming Mail

**Current Behavior:** Gmail Pub/Sub webhook (`gmail_webhook`) receives push notifications, syncs threads, creates notifications, and broadcasts SSE events.

**Required Behavior:** The same flow should work seamlessly for endorsement conversations (type `ENDORSEMENT`, type_based_id `ER-{endorsement_request_id}`). 

**Status:** ✅ Already implemented in `chatmail_controller.py`:
- `_process_new_message()` maps `thread_id` → `ChatConversation` → syncs → sends notifications → broadcasts SSE.
- `_send_notifications_for_new_insurer_messages()` creates notifications with `type_code="email_reply"` and includes `conversation_id`, `insurer_name`, `unread_reply_count` in metadata.

**Verification needed:** Ensure Gmail Watch is set up for the system email and that endorsement-type conversations are being picked up correctly.

---

### 3.2 Real-Time Notification Display

**Current Behavior:** 
- Core UI has `NotificationProvider` which calls `getAllNotification` on mount and provides `reloadNotification()`.
- Core API offers SSE stream at `/api/notifications/stream` and polling at `/api/notifications-unread-count`.
- The `NotificationProvider` does NOT currently connect to SSE or poll periodically.

**Required Changes:**

#### 3.2.1 Enhance NotificationProvider (Core UI)
- **Connect to SSE** (`/api/notifications/stream?token={accessToken}`) for real-time notification push.
- On `new_notification` event, call `reloadNotification()` to refresh the notification list.
- Add **fallback polling** (every 15-30 seconds) for `notifications-unread-count` in case SSE disconnects.
- Track `unreadCount` in the context and expose it for the header badge.

#### 3.2.2 Cross-Module Notification (Policy UI)
- The **Policy UI** also needs to receive these notifications. Since the Policy UI is a separate Next.js app, it needs its own notification context or must connect to the Core API's notification endpoints.
- Add a `NotificationProvider` in the Policy UI that:
  - Polls `/api/notifications-unread-count` periodically.
  - Optionally connects to SSE stream.
  - Provides a notification bell/badge in the Policy UI header.

---

### 3.3 Reply Mail Display in Endorsement Chat

**Current Behavior:**
- `ChatContent.tsx` renders `<Chat>` with `getAllChatMsg`, `createMsgFn`, and `getSyncChatMsg`.
- `getAllChatMsg` calls `GET /api/policy-endorsement/{endorsement_id}/chat?page=X&limit=Y` (Policy API).
- `getSyncChatMsg` calls `GET /api/policy/{policy_id}/sync-endorsement-requests` (Core API) before fetching messages.
- Chat component fetches and displays messages, does initial sync, and supports pagination.

**Required Changes:**

#### 3.3.1 Auto-Refresh Chat on New Mail
- When the user is viewing an endorsement chat and a new mail arrives, the chat should **automatically refresh** to show the new reply.
- Implementation options:
  1. **Polling**: Chat component polls for new messages every 10-15 seconds while visible.
  2. **SSE Integration**: Chat component listens for SSE `new_notification` events and triggers a refresh when the event's `conversation_id` matches.
  3. **Both**: Use SSE as primary, polling as fallback.

#### 3.3.2 Visual Indicator for New Messages
- Show a "New messages" toast/badge when new replies arrive while the chat is open.
- Auto-scroll to bottom when new messages appear (if user is already at the bottom).

#### 3.3.3 Unread Message Count
- Display unread message count on the endorsement request list item.
- Mark messages as `is_seen=true` when the user opens/scrolls through the chat.

---

### 3.4 Chat Polling / Sync Strategy

| Scenario | Strategy |
|----------|----------|
| User opens endorsement chat | Call `getSyncChatMsg` (syncs with Gmail), then `getAllChatMsg` to fetch from DB |
| Chat is open, waiting for reply | Poll `getAllChatMsg` every 10-15s with `sync_thread=false` (fast DB read) |
| New notification received (SSE/poll) | If notification's `conversation_id` matches current chat, trigger re-fetch |
| User sends a message | Call `createMsg`, then refresh chat |

---

## 4. Implementation Tasks

### Phase 1: Backend Verification & Fixes

1. **Verify Gmail Pub/Sub webhook** handles endorsement conversations correctly.
2. **Verify notification creation** for endorsement reply emails (type_code `email_reply`, metadata includes `conversation_id`).
3. **Verify SSE broadcast** triggers for endorsement conversations.
4. **Test manual webhook** via `POST /api/chatmail/gmail-webhook` with `{ "type": "endorsement", "id": <endorsement_request_id>, "mail": "envoy.cloud.services@gmail.com" }`.

### Phase 2: Core UI — NotificationProvider Enhancement

5. **Add SSE connection** to `NotificationProvider.tsx` for real-time updates.
6. **Add polling fallback** for unread count.
7. **Expose unreadCount** in notification context.
8. **Update Header** notification bell to show live unread count.

### Phase 3: Policy UI — Notification Integration

9. **Add NotificationProvider** or equivalent in Policy UI.
10. **Add notification bell/badge** to Policy UI header (using Core API endpoints via proxy).
11. **Auto-refresh endorsement chat** when matching notification event is received.

### Phase 4: Chat Auto-Refresh

12. **Add polling** to `Chat.tsx` for periodic message refresh (configurable interval).
13. **Add SSE listener** in Chat component for real-time updates.
14. **Add "New messages" indicator** when new replies arrive.
15. **Auto-scroll** to new messages when user is at bottom.

### Phase 5: Mark as Read

16. **Mark conversation as seen** when user opens/views endorsement chat.
17. **Update unread count** after marking as read.

---

## 5. API Flow Diagrams

### 5.1 Outgoing Email (Endorsement → Insurer)

```
Policy UI → Policy API → Core API (/api/chatmail/send) → Gmail API
                                    ↓
                         ChatConversation (type=ENDORSEMENT, type_based_id=ER-{id})
                         EmailChatMessage (type=sent, is_seen=true)
```

### 5.2 Incoming Reply (Insurer → System)

```
Gmail → Pub/Sub → Core API (/api/gmail/push-webhook)
                     ↓
              _handle_gmail_history()
                     ↓
              sync_gmail_thread_messages()
                     ↓
              EmailChatMessage (type=received, is_seen=false)
                     ↓
              _send_notifications_for_new_insurer_messages()
                     ↓
              NotificationService.generate_notification()
                     ↓
              broadcast_new_notification (SSE)
                     ↓
              Frontend (SSE/polling) → Notification bell + Chat refresh
```

---

## 6. Modules & Directories to Work In

| Module | Directory | Work |
|--------|-----------|------|
| Core API | `core/envoy-bu-core-api/envoy/` | Verify webhook, notification, SSE |
| Core UI | `core/envoy-bu-core-ui/src/` | Enhance NotificationProvider, Header |
| Policy UI | `policy/envoy-bu-policy-ui/src/` | Chat auto-refresh, notification integration |

---

## 7. Dependencies

- Gmail OAuth configured in `core_gmailcredential` table.
- Gmail Pub/Sub Watch active for the system email.
- Core API running and accessible from Policy API (for chatmail endpoints).
- Proxy configuration in Policy UI's `next.config.mjs` for `CORE_PROXY_PREFIX`.

---

## 8. Status Summary

| # | Task | Status |
|---|------|--------|
| 1 | Requirements documented | ✅ Done |
| 2 | Backend verification | ✅ Done (Verified existing code) |
| 3 | Core UI NotificationProvider enhancement | ✅ Done |
| 4 | Policy UI notification integration | ✅ Done |
| 5 | Chat auto-refresh | ✅ Done |
| 6 | Mark as read | ⬜ Not started |
| 7 | End-to-end testing | ⬜ Not started |
