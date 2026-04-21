import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useRouter } from 'next/navigation';
import { INotification, INotificationDropdownProps } from './_utils/model';
import { getAllNotification } from './_utils/api-service';

// Default pagination settings
const DEFAULT_PAGE_SIZE = 10;

const NotificationDropdown: React.FC<INotificationDropdownProps> = ({ themeMode, hasNotifications }) => {
  const router = useRouter();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const notificationRef = useRef<HTMLDivElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // API state management
  const [notifications, setNotifications] = useState<INotification[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  // Fetch notifications from API
  const fetchNotifications = useCallback(async (page: number = 1, append: boolean = false) => {
    try {
      if (append) {
        setLoadingMore(true);
      } else {
        setLoading(true);
      }
      setError(null);

      const params = {
        page: page.toString(),
        limit: DEFAULT_PAGE_SIZE.toString(),
        sort_by: 'sent_at',
        sort_dir: 'desc',
        read_status: 'all', // Get both read and unread notifications
      };

      const response = await getAllNotification(params);

      if (response && response.is_success && response.result) {
        // Flatten the grouped notifications by date
        const groupedData = response.result.data || [];
        const newNotifications: INotification[] = [];

        groupedData.forEach((group: any) => {
          if (group.notification_data && Array.isArray(group.notification_data)) {
            group.notification_data.forEach((notification: any) => {
              newNotifications.push({
                id: notification.id,
                customer_id: notification.customer_id,
                user_id: notification.user_id,
                type_id: notification.type_id,
                title: notification.title,
                message: notification.message,
                is_read: notification.is_read,
                sent_at: notification.sent_at,
                read_at: notification.read_at,
                metadata: notification.metadata,
                created_at: notification.created_at,
                updated_at: notification.updated_at,
                type_name: notification.type_name,
                type_color: notification.type_color,
                link_id: notification.link_id,
              });
            });
          }
        });

        if (append) {
          setNotifications((prev) => [...prev, ...newNotifications]);
        } else {
          setNotifications(newNotifications);
        }

        setCurrentPage(page);
        setHasMore(newNotifications.length === DEFAULT_PAGE_SIZE);
      } else {
        setError('Failed to fetch notifications');
      }
    } catch (err) {
      setError('An error occurred while fetching notifications');
      console.error('Error fetching notifications:', err);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, []);

  // // Mark notification as read
  // const markAsRead = useCallback(async (notificationId: number) => {
  //     try {
  //         await changeNotificationStatus(notificationId);
  //         // Update local state
  //         setNotifications(prev =>
  //             prev.map(notification =>
  //                 notification.id === notificationId
  //                     ? { ...notification, is_read: 1, read_at: new Date().toISOString() }
  //                     : notification
  //             )
  //         );
  //     } catch (err) {
  //         console.error('Error marking notification as read:', err);
  //     }
  // }, []);

  // Load more notifications (infinite scroll)
  const loadMoreNotifications = useCallback(() => {
    if (!loadingMore && hasMore) {
      fetchNotifications(currentPage + 1, true);
    }
  }, [currentPage, hasMore, loadingMore, fetchNotifications]);

  // Handle scroll for infinite loading
  const handleScroll = useCallback(
    (e: React.UIEvent<HTMLDivElement>) => {
      const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
      const threshold = 50; // Load more when 50px from bottom

      if (scrollHeight - scrollTop <= clientHeight + threshold) {
        loadMoreNotifications();
      }
    },
    [loadMoreNotifications],
  );

  const handleNotificationIconClick = () => {
    setIsDropdownOpen(!isDropdownOpen);
    // Fetch notifications when dropdown opens
    if (!isDropdownOpen && notifications.length === 0) {
      fetchNotifications(1, false);
    }
  };

  const handleNotificationItemClick = async (notificationId: number) => {
    // const notification = notifications.find(n => n.id === notificationId);
    // if (notification) {
    //     // Mark as read if not already read
    //     if (notification.is_read === 0) {
    //         await markAsRead(notificationId);
    //     }

    //     // Navigate based on link_id if available
    //     if (notification.link_id > 0) {
    //         // You can customize the navigation based on notification type
    //         switch (notification.type_name.toLowerCase()) {
    //             case 'policy':
    //                 router.push(`/a/policies/${notification.link_id}`);
    //                 break;
    //             case 'quotation':
    //                 router.push(`/a/quotations/${notification.link_id}`);
    //                 break;
    //             case 'message':
    //                 router.push(`/a/messages/${notification.link_id}`);
    //                 break;
    //             case 'payment':
    //                 router.push(`/a/payments/${notification.link_id}`);
    //                 break;
    //             case 'user':
    //                 router.push(`/a/users/${notification.link_id}`);
    //                 break;
    //             case 'report':
    //                 router.push(`/a/reports/${notification.link_id}`);
    //                 break;
    //             default:
    //                 router.push(`/a/notifications/${notification.id}`);
    //         }
    //     } else {
    //         // Navigate to notification details page
    //         router.push(`/a/notifications/${notification.id}`);
    //     }
    //     setIsDropdownOpen(false);
    // }
    console.log(notificationId);
  };

  const handleViewAllClick = () => {
    router.push('/a/notifications?t=all');
    setIsDropdownOpen(false);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    if (isDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isDropdownOpen]);

  const getNotificationIcon = (typeName: string) => {
    switch (typeName.toLowerCase()) {
      case 'policy':
        return 'file-check-02';
      case 'quotation':
        return 'file-02';
      case 'payment':
        return 'credit-card-02';
      case 'message':
        return 'message-circle-02';
      case 'system':
        return 'settings-02';
      case 'user':
        return 'user-02';
      case 'report':
        return 'file-02';
      case 'backup':
        return 'database-02';
      case 'security':
        return 'alert-triangle';
      case 'maintenance':
        return 'info-circle';
      default:
        return 'bell-02';
    }
  };

  const formatTimeAgo = (sentAt: string) => {
    const now = new Date();
    const sentTime = new Date(sentAt);
    const diffInSeconds = Math.floor((now.getTime() - sentTime.getTime()) / 1000);

    if (diffInSeconds < 60) {
      return `${diffInSeconds} seconds ago`;
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60);
      return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600);
      return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    } else if (diffInSeconds < 604800) {
      const days = Math.floor(diffInSeconds / 86400);
      return `${days} day${days > 1 ? 's' : ''} ago`;
    } else {
      const weeks = Math.floor(diffInSeconds / 604800);
      return `${weeks} week${weeks > 1 ? 's' : ''} ago`;
    }
  };

  return (
    <div className="position-relative" ref={notificationRef}>
      {/* Notification Icon */}
      <div className="notification-icon btn btn-outline-light border-0 position-relative d-flex align-items-center justify-content-center p-2 rounded-3" onClick={handleNotificationIconClick}>
        <Flexicon icon="bell-02" variant="line" />
        {hasNotifications && (
          <span className={`notification-badge position-absolute ${themeMode === 'dark' ? 'notification-badge-dark' : 'notification-badge-light'}`}>
            <span className="visually-hidden">New notifications</span>
          </span>
        )}
      </div>

      {/* Notification Dropdown */}
      {isDropdownOpen && (
        <div className={`notification-dropdown ${themeMode === 'dark' ? 'notification-dropdown-dark' : ''}`}>
          <div className="notification-dropdown-header">
            <h6 className="mb-0">Notifications</h6>
            <div className="text-primary pointer fw-semibold fs-14" onClick={handleViewAllClick}>
              View All
            </div>
          </div>
          <div className="notification-dropdown-content" ref={scrollRef} onScroll={handleScroll}>
            {loading ? (
              <div className="notification-loading">
                <div className="spinner-border spinner-border-sm text-primary" role="status">
                  <span className="visually-hidden">Loading...</span>
                </div>
                <p className="text-muted mb-0 mt-2">Loading notifications...</p>
              </div>
            ) : error ? (
              <div className="notification-error">
                <Flexicon icon="alert-triangle" variant="line" size={32} className="text-danger mb-2" />
                <p className="text-danger mb-0">{error}</p>
                <button className="btn btn-sm btn-outline-primary mt-2" onClick={() => fetchNotifications(1, false)}>
                  Try Again
                </button>
              </div>
            ) : notifications.length > 0 ? (
              <>
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={`notification-item ${notification.is_read === 0 ? 'notification-item-unread' : ''}`}
                    onClick={() => handleNotificationItemClick(notification.id)}
                  >
                    <div
                      className="notification-item-icon"
                      style={{
                        backgroundColor: `${notification.type_color}15`,
                        border: `1px solid ${notification.type_color}30`,
                      }}
                    >
                      <Flexicon icon={getNotificationIcon(notification.type_name)} variant="line" size={16} />
                    </div>
                    <div className="notification-item-content">
                      <div className="notification-item-title">{notification.title}</div>
                      <div className="notification-item-message">{notification.message}</div>
                      <div className="notification-item-time">{formatTimeAgo(notification.sent_at)}</div>
                    </div>
                    {notification.is_read === 0 && <div className="notification-item-dot"></div>}
                  </div>
                ))}

                {/* Loading more indicator */}
                {loadingMore && (
                  <div className="notification-loading-more">
                    <div className="spinner-border spinner-border-sm text-primary" role="status">
                      <span className="visually-hidden">Loading more...</span>
                    </div>
                    <span className="text-muted ms-2">Loading more...</span>
                  </div>
                )}

                {/* No more notifications indicator */}
                {!hasMore && notifications.length > 0 && (
                  <div className="notification-no-more">
                    <p className="text-muted mb-0">No more notifications</p>
                  </div>
                )}
              </>
            ) : (
              <div className="notification-empty">
                <Flexicon icon="bell-02" variant="line" size={32} className="text-muted mb-2" />
                <p className="text-muted mb-0">No notifications</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationDropdown;
