# Notifications API – How the Frontend Fetches Them (Including “Live”)

## Flow

1. **Backend**: When a reply is received at `envoy.cloud.services@gmail.com`, the Gmail watch triggers the webhook → messages are synced and stored with `is_seen=false` → a notification row is created and linked to the user in `core_notification_users` → a **real-time event** is pushed to any connected SSE clients for that user.
2. **Frontend**: For **real-time** updates, connect to **GET** `/api/notifications/stream` (Server-Sent Events). When you receive a `new_notification` event, call **GET** `/api/all-notifications` to refresh the list. You can also use **polling** (e.g. `/api/notifications-unread-count` every 15–30 seconds) as a fallback.

---

## Endpoints for the Frontend

### 0. Real-time stream (SSE) – recommended for live updates

**GET** `/api/notifications/stream`

**Auth**: Required. Because `EventSource` cannot send headers, pass the JWT in the query string:  
`/api/notifications/stream?token=<your_access_token>`

**Response**: Server-Sent Events stream (`Content-Type: text/event-stream`). Events:

- **`new_notification`** – A new notification was created for this user (e.g. new mail received). Payload: `{"event": "new_notification", "user_id": 1}`. When you receive this, call **GET** `/api/all-notifications` to refresh the list and update the UI.
- **`: heartbeat`** – Comment line sent periodically to keep the connection alive; ignore it.

**Frontend example (real-time list update):**

```javascript
// After login, you have accessToken
const streamUrl = `${API_BASE}/api/notifications/stream?token=${encodeURIComponent(accessToken)}`;
const evtSource = new EventSource(streamUrl);

evtSource.onmessage = (e) => {
  const data = JSON.parse(e.data);
  if (data.event === 'new_notification') {
    // New mail/notification received – refresh the list
    fetch(`${API_BASE}/api/all-notifications`, {
      headers: { Authorization: `Bearer ${accessToken}` }
    })
      .then(res => res.json())
      .then(result => {
        if (result.is_success && result.result) {
          // Update your notifications state with result.result
          setNotifications(result.result);
        }
      });
    // Optionally refresh unread count / badge
  }
};

evtSource.onerror = () => {
  // Reconnect or fall back to polling
};
```

When the Gmail webhook creates a notification (e.g. new reply), the backend pushes to this stream so the UI can refresh **immediately** without polling.

---

### 1. Unread count (for live badge / polling)

**GET** `/api/notifications-unread-count`

**Auth**: Required (same as rest of app).

**Response**:
```json
{
  "is_success": true,
  "message": "unread_count",
  "unread_count": 3
}
```

**Usage**: Poll this every **15–30 seconds** (or when the app gains focus) to update a notification badge. When `unread_count > 0` or when the user opens the notifications panel, call the list endpoint to load the actual notifications.

---

### 2. List notifications (full list / when user opens panel)

**GET** `/api/all-notifications`

**Query params** (all optional):

| Param         | Description                                      |
|---------------|--------------------------------------------------|
| `page`        | Page number (default: 1)                        |
| `limit`       | Items per page (default: 10)                     |
| `read_status` | `"read"` \| `"unread"` – filter by read state   |
| `filter`      | `"today"` \| `"last_week"` \| `"last_month"`    |
| `sort_by`     | e.g. `core_notification_users.id`               |
| `sort_dir`    | `asc` \| `desc`                                 |

**Response**:
```json
{
  "is_success": true,
  "message": "notifications_retrieved",
  "result": {
    "total_records": 5,
    "per_page": 10,
    "current_page": 1,
    "last_page": 1,
    "data": [
      {
        "date": "12 Mar 2025",
        "notification_data": [
          {
            "id": 123,
            "notification_id": 456,
            "title": "New reply from Acme Insurer",
            "message": "You received 2 reply messages for this conversation.",
            "notification_code": "email_reply",
            "read_status": "unread",
            "metadata": "{\"conversation_id\":\"42\",\"conversation_code\":\"ABC123\",\"unread_reply_count\":2,\"insurer_name\":\"Acme Insurer\"}",
            "created_at": "2025-03-12 10:30:00",
            "type_color": "#4CAF50"
          }
        ]
      }
    ]
  }
}
```

For **email reply** notifications (`notification_code === "email_reply"`), parse `metadata` (JSON) to get:

- `conversation_id` – use for deep link to that chat
- `conversation_code` – display or API use
- `unread_reply_count` – number of new replies
- `insurer_name` – insurer name

---

### 3. Mark as read

**POST** `/api/read-notifications/<ids>`

**Path**: `ids` = comma-separated list of **`core_notification_users.id`** (the `id` from each item in `notification_data`), e.g. `123,124`.

**Usage**: Call when the user opens a notification or the notifications panel so the badge and list reflect “read”.

---

### 4. Single notification detail

**GET** `/api/notifications/<notification_id>`

**Path**: `notification_id` = `core_notifications.id` (e.g. the `notification_id` from the list, here `456`).

**Usage**: When the user taps a notification, open the conversation using `metadata.conversation_id` and optionally load this endpoint if you need full detail.

---

## Suggested “live” behaviour in the frontend

1. **Background**: Every 15–30 seconds (or on window focus), call **GET** `/api/notifications-unread-count`. Update the bell/badge with `unread_count`.
2. **When user opens the notifications panel**: Call **GET** `/api/all-notifications` (optionally with `read_status=unread` and `limit=20`) to show the list. Optionally mark visible items as read via **POST** `/api/read-notifications/<ids>`.
3. **When user taps an email reply notification**: Parse `metadata.conversation_id` and navigate to that conversation; optionally call **POST** `/api/read-notifications/<id>` for that notification so it becomes read.

This way, new reply notifications created by the webhook are shown “live” via the polling unread count and the list when the user opens the panel.

---

## Automatic refresh when new mail is received (near real-time)

The backend cannot call the frontend. To make the UI **automatically** call `/api/all-notifications` when new mail arrives (so the list updates in near real-time), the frontend should:

1. **Poll unread count**  
   Every **5–15 seconds** (e.g. 10 seconds), call **GET** `/api/notifications-unread-count`.

2. **Detect “new mail”**  
   Keep the **previous** `unread_count` in state. If the **current** `unread_count` is **greater** than the previous value, treat it as “new mail received”.

3. **Auto-call list endpoint**  
   When you detect an increase in `unread_count`:
   - **Automatically** call **GET** `/api/all-notifications` to refresh the notification list (e.g. refetch the first page or the current view).
   - If the notifications panel is open, replace/append the list with the new response so new items appear without the user refreshing.
   - Update the badge with the new `unread_count`.

4. **Optional: refresh list while panel is open**  
   While the notifications panel is visible, you can also poll **GET** `/api/all-notifications` every 10–15 seconds so the list stays up to date even if the unread-count logic is not triggered.

**Result**: When new mail is received, within one poll interval (e.g. 10 seconds) the frontend will see the higher unread count, automatically call `/api/all-notifications`, and the UI will show the new notification without the user opening the panel or refreshing.

---

## Real-time via SSE (when new mail is received)

When a new email is received and the Gmail Pub/Sub webhook runs, the backend:

1. Creates the notification and inserts into `core_notifications` / `core_notification_users`.
2. Pushes a **`new_notification`** event to all connected SSE clients for that user (see **GET** `/api/notifications/stream` above).

So if the frontend keeps an **EventSource** open to `/api/notifications/stream?token=...`, it will receive the event as soon as the notification is created. On that event, call **GET** `/api/all-notifications` and update the UI so the new notification appears in real time without polling.
