export interface INotification {
  id: number;
  customer_id: number;
  user_id: number;
  type_id: number;
  title: string;
  message: string;
  is_read: number;
  sent_at: string;
  read_at?: string;
  metadata: string;
  created_at: string;
  updated_at: string;
  type_name: string;
  type_color: string;
  link_id: number;
}

export interface INotificationDropdownProps {
  themeMode: 'light' | 'dark';
  hasNotifications: boolean;
  notifications?: INotification[];
  onNotificationClick?: (notificationId: number) => void;
  onViewAllClick?: () => void;
}
