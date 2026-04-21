export interface INotificationData {
  date: string;
  notification_data: INotification[];
}

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
