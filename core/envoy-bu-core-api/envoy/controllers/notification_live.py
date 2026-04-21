"""
In-memory broadcaster for real-time notification events (SSE).
When a new notification is created (e.g. from Gmail webhook), we push an event
so connected frontends can refetch GET /api/all-notifications.
"""
import json
import threading
import queue

# user_id -> list of queues (each queue is for one SSE client)
_subscribers = {}
_lock = threading.Lock()
# Heartbeat interval (seconds) so client knows connection is alive
HEARTBEAT_INTERVAL = 25


def subscribe(user_id):
    """Register a new SSE client for this user. Returns a queue that will receive event dicts."""
    q = queue.Queue()
    with _lock:
        if user_id not in _subscribers:
            _subscribers[user_id] = []
        _subscribers[user_id].append(q)
    return q


def unsubscribe(user_id, q):
    """Remove this client's queue."""
    with _lock:
        if user_id in _subscribers:
            try:
                _subscribers[user_id].remove(q)
            except ValueError:
                pass
            if not _subscribers[user_id]:
                del _subscribers[user_id]


def broadcast_new_notification(user_id):
    """
    Call this when a new notification is created for user_id (e.g. from NotificationService).
    All connected SSE clients for this user will receive a 'new_notification' event.
    """
    event = {"event": "new_notification", "user_id": user_id}
    with _lock:
        queues = list(_subscribers.get(user_id) or [])
    for q in queues:
        try:
            q.put_nowait(event)
        except Exception:
            pass
