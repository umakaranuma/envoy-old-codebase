'use client';
import 'react-big-calendar/lib/css/react-big-calendar.css';
import React, { useEffect, useMemo, useState } from 'react';
import { Calendar as BigCalendar, momentLocalizer, Views, View } from 'react-big-calendar';
import moment from 'moment';
import { fetchAllAssignees } from '../../../service';
import { useAsyncTable } from '@apptimus-ui/table';
import S3Avatar from '@/components/others/page-related/S3Avatar';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useTrans } from '@/helpers/services/lang/langService';
import Table from '@/components/table-properties/Table';
import { Flexicon } from '@apptimus-ui/flexicon';
import { getAllTaskCalender } from '../../../api-service';
import { hasPermission } from '@/components/others/Permission';
import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';
import { useRouter } from 'next/navigation';

function CalendarView() {
  const t = useTrans('label.tasks');
  const [currentView, setCurrentView] = useState<View>(Views.MONTH);
  const localizer = momentLocalizer(moment);
  const [events, setEvents] = useState<any[]>();
  const [date, setDate] = useState(new Date());
  const [selectedAssignee, setSelectedAssignee] = useState('');
  const userTaskViewAllPerm = hasPermission('TASK', ['VIEW_ALL']);
  const router = useRouter();

  useEffect(() => {
    if (!userTaskViewAllPerm) {
      const authUser = getLocalStorage(local_storage.auth_user_info);
      if (authUser) {
        setSelectedAssignee(authUser.id);
      }
    }
  }, []);

  const handleNavigate = (newDate: Date) => {
    setDate(newDate);
  };

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'name',
        header: t('users'),
        accessorKey: 'name',
        cell: ({ cell, onClick }: { cell: any; onClick: Function }) => {
          return (
            <div role="button" className="d-flex flex-row align-items-center gap-2" onClick={() => onClick()}>
              <div>
                <S3Avatar imageKey={undefined} width={35} height={35} />
              </div>
              <div className="fs-14 fw-medium">{cell.display_name}</div>
            </div>
          );
        },
        size: '15rem',
      },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: fetchAllAssignees,
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
      action: (id: string) => setSelectedAssignee(id),
    },
  });

  // const formattedEvent = response.data?.data.map((event: IEvent) => (
  //     {
  //         id: event._id,
  //         title: event.name,
  //         start: new Date(event.startDateAndTime),
  //         end: new Date(event.endDateAndTime),
  //         description: event.description,
  //     }
  // ))
  // setEvents(formattedEvent)
  // const CustomDateCell = ({ label, date }:any) => {
  //     return (
  //         <div className="d-flex flex-row justify-content-between align-items-center">
  //             <div>{label}</div>
  //         </div>
  //     );
  // };

  useEffect(() => {
    const fetchEvents = async () => {
      const fromDate = moment(date).startOf('month').format('YYYY-MM-DD');
      const toDate = moment(date).endOf('month').format('YYYY-MM-DD');
      const response = await getAllTaskCalender(fromDate, toDate, selectedAssignee);
      if (response.is_success) {
        setEvents(response.result);
      }
    };
    if (selectedAssignee !== '') {
      fetchEvents();
    }
  }, [selectedAssignee]);

  const CustomToolbar = ({ label, onNavigate }: any) => {
    return (
      <div className="d-flex justify-content-between align-items-center mb-3">
        {/* <span className="rbc-btn-group pointer">
          <div onClick={() => onNavigate('TODAY')}>Today</div>
        </span> */}
        <span className="rbc-toolbar-label pointer">
          <div className="rbc-toolbar-label-arrow shadow-sm rounded-circle" onClick={() => onNavigate('PREV')}>
            <Flexicon icon="chevron-left" variant="line" size={30} />
          </div>
          <div className="text-primary fw-medium">{label}</div>
          <div className="rbc-toolbar-label-arrow shadow-sm rounded-circle" onClick={() => onNavigate('NEXT')}>
            <Flexicon icon="chevron-right" variant="line" size={30} />
          </div>
        </span>
        <span className="d-flex justify-content-between align-items-center gap-1 pointer">
          {/* <Button
            type="button"
            className={currentView === "year" ? "rbc-active" : ""}
            onClick={() => setCurrentView("year")}
          >
            Year
          </Button> */}
          {/* <div className={`${currentView === 'week' ? 'rbc-active' : ''} rbc-btn-group-button border-radius-start`} onClick={() => setCurrentView('week')}>
            Week
          </div> */}
          <div className={`${currentView === 'month' ? 'rbc-active' : ''} rbc-btn-group-button rbc-btn-group`} onClick={() => setCurrentView('month')}>
            Month
          </div>
          {/* <div className={`${currentView === 'day' ? 'rbc-active' : ''} rbc-btn-group-button border-radius-end`} onClick={() => setCurrentView('day')}>
            Day
          </div> */}
        </span>
      </div>
    );
  };

  return (
    <div className="d-flex gap-3 mt-2">
      {userTaskViewAllPerm && (
        <div className="bg-white rounded-3 shadow-sm p-2">
          <Table {...{ tableProperties, isRowPerPageVisible: false, searchOption: false, isPaginationTextVisible: false }} />
        </div>
      )}
      <div className="col-lg-9 col-md-12">
        <div className="bg-white p-3 rounded-3">
          <BigCalendar
            key={selectedAssignee}
            localizer={localizer}
            style={{ height: 500 }}
            events={events}
            views={[Views.MONTH, Views.WEEK, Views.DAY]}
            view={currentView}
            onView={(view) => setCurrentView(view)}
            date={date}
            onNavigate={handleNavigate}
            onSelectEvent={(event) => console.log(event.id)}
            components={{
              toolbar: CustomToolbar,
              event: ({ event }) => (
                <div className="" onClick={() => router.push(`tasks/${event.id}`)}>
                  <div className="d-flex align-items-center gap-3 fs-12 fw-medium">
                    {/* <div>{moment(event.start).format('hh:mm')}</div>
                  <div>{moment(event.end).format('hh:mm')}</div> */}
                  </div>
                  <div className="fw-medium fs-11">{event.title}</div>
                </div>
              ),
              // month: {
              //   dateHeader: CustomDateCell, // Customizing date cell in Month view
              // },
            }}
          />
        </div>
      </div>
    </div>
  );
}

export default CalendarView;
