import { getAllNotification } from '@/app/[appId]/a/notifications/_utils/api-service';
import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';

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
  // getNotification: (readStatus?: string, filter?: string) => Promise<INotification[]>;
}

const NotificationContext = createContext<NotificationContextType | null>(null);

function NotificationProvider({ children }: { children: React.ReactNode }) {
  const [notifications, setNotifications] = useState<INotification[]>([]);

  const setNotification = useCallback((notifications: INotification[]) => {
    setNotifications(notifications);
  }, []);

  // const getNotification = useCallback(async (readStatus?: string, filter?: string) => {
  //     const responseData = await getAllNotification({ read_status: readStatus ? readStatus : '', filter: filter ? filter : '' });
  //     if (responseData.is_success) {
  //         return (responseData.result.data);
  //     } else {
  //         return ([]);
  //     }
  // }, [notifications])

  const reloadNotification = useCallback(async (readStatus?: string, filter?: string) => {
    const responseData = await getAllNotification({ read_status: readStatus ? readStatus : 'unread', filter: filter ? filter : '' });
    if (responseData.is_success) {
      setNotifications(responseData.result.data);
    } else {
      console.error(responseData.message);
    }
  }, []);

  useEffect(() => {
    reloadNotification();
  }, [reloadNotification]);

  return <NotificationContext.Provider value={{ notifications, setNotification, reloadNotification }}>{children}</NotificationContext.Provider>;
}

export default NotificationProvider;

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
};
