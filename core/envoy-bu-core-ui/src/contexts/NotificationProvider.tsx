import { getAllNotification, getUnreadNotificationCount } from '@/app/a/notifications/_utils/api-service';
import React, { createContext, useCallback, useContext, useEffect, useState, useRef } from 'react';

export interface INotification {
  date: string;
  notification_data: Notification[];
}

interface Notification {
  id: number;
  notification_id: number;
  user_id: number;
  customer_id: number;
  is_read: number;
  is_clear: number;
  read_at: null;
  type_id: number;
  title: string;
  message: string;
  sent_at: Date;
  metadata: string;
  created_at: Date;
  updated_at: Date;
  notification_code: string;
  notification_name: string;
  type_color: string;
  type_name: string;
  read_status: string;
  link_id: number | null;
}

interface NotificationContextType {
  notifications: INotification[];
  setNotification: (notifications: INotification[]) => void;
  reloadNotification: (readStatus?: string, filter?: string) => Promise<void>;
  unreadCount: number;
}

const NotificationContext = createContext<NotificationContextType | null>(null);

function NotificationProvider({ children, token }: { children: React.ReactNode; token?: string }) {
  const [notifications, setNotifications] = useState<INotification[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const unreadCountRef = useRef<number>(0);

  const setNotification = useCallback((notifications: INotification[]) => {
    setNotifications(notifications);
  }, []);

  const fetchUnreadCount = useCallback(async () => {
    const responseData = await getUnreadNotificationCount();
    if (responseData.is_success) {
      const newCount = responseData.result?.unread_count || 0;
      if (newCount > unreadCountRef.current) {
        // Auto-refresh notifications if unread count increased
        reloadNotification();
      }
      setUnreadCount(newCount);
      unreadCountRef.current = newCount;
    }
  }, []);

  const reloadNotification = useCallback(async (readStatus?: string, filter?: string) => {
    const responseData = await getAllNotification({ read_status: readStatus ? readStatus : 'unread', filter: filter ? filter : '' });
    if (responseData.is_success) {
      setNotifications(responseData.result.data);
    } else {
      console.error(responseData.message);
    }
    // Also update unread count whenever list is reloaded
    fetchUnreadCount();
  }, [fetchUnreadCount]);

  useEffect(() => {
    reloadNotification();
  }, [reloadNotification]);

  // Polling fallback
  useEffect(() => {
    const interval = setInterval(() => {
      fetchUnreadCount();
    }, 20000); // 20 seconds
    return () => clearInterval(interval);
  }, [fetchUnreadCount]);

  // Real-time SSE
  useEffect(() => {
    if (!token) return;

    let eventSource: EventSource | null = null;
    let reconnectTimeout: NodeJS.Timeout | null = null;

    const connectSSE = () => {
      // Use absolute API URL or fall back to standard browser host based routing
      const baseUrl = process.env.NEXT_PUBLIC_CORE_API_URL || '';
      const url = `${baseUrl}/api/notifications/stream?token=${encodeURIComponent(token)}`;
      try {
        eventSource = new EventSource(url);

        eventSource.onmessage = (e) => {
          try {
            const data = JSON.parse(e.data);
            if (data.event === 'new_notification') {
              // Refresh everything
              reloadNotification();
            }
          } catch (error) {
            console.error('Error parsing SSE data', error);
          }
        };

        eventSource.onerror = () => {
          eventSource?.close();
          // Attempt to reconnect later
          reconnectTimeout = setTimeout(connectSSE, 5000);
        };
      } catch (err) {
        console.error('SSE connection failed', err);
      }
    };

    connectSSE();

    return () => {
      if (eventSource) eventSource.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, [token, reloadNotification]);

  return <NotificationContext.Provider value={{ notifications, setNotification, reloadNotification, unreadCount }}>{children}</NotificationContext.Provider>;
}

export default NotificationProvider;

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
};
