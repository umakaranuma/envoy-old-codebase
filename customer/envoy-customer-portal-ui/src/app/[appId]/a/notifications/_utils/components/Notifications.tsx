'use client';
import React, { useEffect, useState } from 'react';
import { useNotificationTableProperty } from './NotificationsTableProperty';
import { useTrans } from '@/helpers/services/lang/langService';
import { Button, Skeleton } from '@apptimus-ui/ui-element';
import RecordController from '@/components/table-properties/RecordController';
import { Flexicon } from '@apptimus-ui/flexicon';
import { formatDate, getNotificationTime, hexToRgba } from '@/helpers/services/commonService';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { INotification, INotificationData } from '../model';
import { changeNotificationStatus } from '../api-service';
import { toaster } from '@/helpers/services/toaster';
import { useNotification } from '@/hooks/NotificationProvider';

function Notifications() {
  const t = useTrans('label.notifications,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [activeTab, setActiveTab] = useState('all');
  const [filter, setFilter] = useState('all');
  const { tableProperties } = useNotificationTableProperty({ read_status: activeTab, filter: filter === 'all' ? '' : filter });
  const [notificationData, setNotificationData] = useState<INotificationData[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const searchParams = useSearchParams();
  const router = useRouter();
  const params = useParams();
  const appId = params.appId as string;
  const { reloadNotification } = useNotification();

  useEffect(() => {
    console.log('selectedIds', selectedIds);
  }, [selectedIds]);

  useEffect(() => {
    setSelectedIds([]);
  }, [activeTab]);

  // Clear selected items when filter changes as well
  useEffect(() => {
    setSelectedIds([]);
  }, [filter]);

  useEffect(() => {
    const tab = searchParams.get('t') || 'all';
    toggleTableTab(tab);
  }, []);

  useEffect(() => {
    setNotificationData(tableProperties.tableData);
  }, [tableProperties, activeTab, filter]);

  const toggleTableTab = (activeTab: string) => {
    setActiveTab(activeTab);
    router.push(`/${appId}/a/notifications?t=${activeTab}`, { scroll: false });
  };

  const handleSelectedIds = (id: number) => {
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((selectedId) => selectedId !== id) : [...prev, id]));
  };

  // Compute all IDs currently displayed for the active tab/filter
  const allDisplayedIds = React.useMemo(() => {
    try {
      return notificationData.flatMap((group) => group.notification_data.map((n) => n.id));
    } catch {
      return [] as number[];
    }
  }, [notificationData]);

  const isAllSelected = allDisplayedIds.length > 0 && allDisplayedIds.every((id) => selectedIds.includes(id));

  const handleToggleSelectAll = () => {
    if (isAllSelected) {
      setSelectedIds([]);
    } else {
      setSelectedIds(allDisplayedIds);
    }
  };

  async function handleMarkAsRead() {
    setIsFormProcessing(true);

    try {
      const responseData = await changeNotificationStatus(selectedIds.join(','));
      setIsFormProcessing(false);

      if (responseData.is_success) {
        reloadNotification('unread', '');
        setSelectedIds([]);
        tableProperties.reload();
        router.refresh();
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  // const handleDeleteNotification = async (id: number) => {
  //   try {
  //     const responseData = await deleteNotification(id.toString());
  //     setIsFormProcessing(false);

  //     if (responseData.is_success) {
  //       tableProperties.reload();
  //       toaster.success(tBe(responseData.message));
  //     }
  //   } catch (error) {
  //     console.error('An error occurred:', error);
  //   }
  // };

  // useEffect(() => {
  //   console.log('selectedIds', selectedIds);
  // }
  //   , [selectedIds]);
  return (
    <div className="panel mt-5 p-4">
      <div className="mb-4 d-flex flex-row flex-wrap gap-2 align-items-center justify-content-between">
        <div className="px-1 bg-light rounded-2" style={{ width: 'fit-content' }}>
          <div className="d-flex flex-row gap-1 overflow-x-auto text-nowrap py-1" style={{ scrollbarWidth: 'none' }}>
            <div
              style={{ paddingTop: '7px', paddingBottom: '7px' }}
              className={`fw-medium pointer px-4 ${activeTab === 'all' ? 'rounded bg-white ' : 'text-muted'}`}
              onClick={() => toggleTableTab('all')}
            >
              {t('all')}
            </div>
            <div
              style={{ paddingTop: '7px', paddingBottom: '7px' }}
              className={`fw-medium pointer px-4 ${activeTab === 'unread' ? 'rounded bg-white ' : 'text-muted'}`}
              onClick={() => toggleTableTab('unread')}
            >
              {t('unread')}
            </div>
            <div
              style={{ paddingTop: '7px', paddingBottom: '7px' }}
              className={`fw-medium pointer px-4 ${activeTab === 'read' ? 'rounded bg-white ' : 'text-muted'}`}
              onClick={() => toggleTableTab('read')}
            >
              {t('read')}
            </div>
          </div>
        </div>
        <div className="d-flex flex-row gap-2 align-items-center justify-content-between">
          {activeTab === 'unread' && (
            <Button variant="outline" color="light" className="d-flex align-items-center gap-1 border border-2 border-muted" onClick={handleToggleSelectAll}>
              {isAllSelected ? 'Unselect All' : 'Select All'}
            </Button>
          )}
          <Dropdown
            trigger={
              <Button variant="light" color="light" className="d-flex align-items-center gap-1 border border-2 border-muted">
                <Flexicon icon="calendar" variant="line" size={15} />
                <span>{t(`${filter === 'all' ? 'all' : filter === 'today' ? 'today' : filter === 'last_week' ? 'last_week' : 'last_month'}`)}</span>
                <Flexicon icon="chevron-down" variant="line" size={15} />
              </Button>
            }
          >
            {(onClose: Function) => (
              <>
                <DropdownItem onClick={() => (setFilter('all'), onClose())}>
                  <span>{t('all')}</span>
                </DropdownItem>
                <DropdownItem onClick={() => (setFilter('today'), onClose())}>
                  <span>{t('today')}</span>
                </DropdownItem>
                <DropdownItem onClick={() => (setFilter('last_week'), onClose())}>
                  <span>{t('last_week')}</span>
                </DropdownItem>
                <DropdownItem onClick={() => (setFilter('last_month'), onClose())}>
                  <span>{t('last_month')}</span>
                </DropdownItem>
              </>
            )}
          </Dropdown>
          {activeTab !== 'read' && selectedIds.length > 0 && <Button text={t('mark_as_read')} variant="outline" onClick={handleMarkAsRead} isLoading={isFormProcessing} />}
        </div>
      </div>
      <div className="d-flex flex-column gap-3">
        {tableProperties.isTbodyLoading ? (
          <Skeleton height="60px" width="100%" />
        ) : (
          <>
            {notificationData.length > 0 ? (
              <>
                {notificationData.map((notification: INotificationData, index: number) => (
                  <div className="mb-2" key={index}>
                    <div className="fw-medium border-bottom border-light pb-2">{formatDate(notification.date)}</div>
                    {notification.notification_data.map((data: INotification, itemIndex: number) => (
                      <div
                        className="d-flex flex-row flex-wrap flex-md-nowrap gap-3 align-items-center justify-content-between px-3 py-2 border border-2 border-muted rounded-2 my-2 mt-3"
                        key={itemIndex}
                      >
                        <div className="d-flex flex-row gap-3 align-items-center justify-content-between">
                          {activeTab === 'unread' && (
                            <div>
                              <input
                                type="checkbox"
                                style={{ transform: 'scale(1.5)', margin: '5px', accentColor: '#088AB2' }}
                                checked={selectedIds.includes(data.id)}
                                onChange={() => handleSelectedIds(data.id)}
                              />
                            </div>
                          )}
                          <div>
                            <div className="d-flex flex-row gap-2 align-items-center">
                              <div className="fw-medium mb-1">{data.title}</div>
                              <div
                                className={`rounded-5 fw-semibold px-2 fs-12`}
                                style={{
                                  background: hexToRgba(data.type_color, 0.1),
                                  border: `1px solid ${hexToRgba(data.type_color, 0.4)}`,
                                  color: data.type_color,
                                }}
                              >
                                {data.type_name.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                              </div>
                              <span className="ms-2 fs-12">{getNotificationTime(data.created_at)}</span>
                            </div>
                            <div className="text-muted fs-14">{data.message}</div>
                          </div>
                        </div>
                        {/* <div className="d-flex flex-row gap-2 align-items-center justify-content-end">
                          <Flexicon icon="eye" variant="line" size={30} className="bg-primary icon-button text-white" onClick={() => { }} />
                          <Flexicon icon="trash-01" variant="line" size={30} className="bg-danger icon-button text-white " onClick={() => handleDeleteNotification(data.id)} />
                        </div> */}
                      </div>
                    ))}
                  </div>
                ))}
                <RecordController tableProperties={tableProperties} isRowPerPageVisible={true} isPaginationTextVisible={true} isPaginationButtonVisible={true} />
              </>
            ) : (
              <div className="text-muted text-center fs-16 fw-semibold">No records found!</div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default Notifications;
