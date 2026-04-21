import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useReducer, useState } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import { fetchAllTaskTableData } from '../../service';
import { Skeleton } from '@apptimus-ui/ui-element';
import { convertToMap, convertToString, formatDate, hexToRgba } from '@/helpers/services/commonService';
import { changeTaskStatus, getManyOpportunities } from '../../api-service';
import { dataReducer, filterReducer } from '@/helpers/services/dataReducer';
import { getAllTaskStatuses } from '@/api-services/common';
import { useRouter } from 'next/navigation';
import TaskFilter from './TaskFilter';

function AssignedTasksList({ tableVers, onView, onEdit, handleOnDelete, opId = '' }: { tableVers: number; onView: Function; onEdit: Function; handleOnDelete: Function; opId?: string }) {
  const t = useTrans('label.tasks,otr.common');
  const tableName = 'tasks';
  const router = useRouter();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const [opData, opDispatch] = useReducer(dataReducer, { loadingState: true, columnKeyVers: 0, data: {} });
  const [taskStatus, setTaskStatus] = useState<{ id: string; name: string }[]>([]);
  const [tVers, setTVers] = useState(0);
  const [isFilterVisible, setIsFilterVisible] = useState(false);
  const [filterComKey, setFilterComKey] = useState(0);

  const handleChangeStatus = async (id: string, statusId: string) => {
    const response = await changeTaskStatus(id, { status_id: statusId });
    if (response.is_success) {
      setTaskStatus(response.result);
      setTVers((prevVers) => prevVers + 1);
    }
  };

  const columns = useMemo<ITablePropertyColumn[]>(() => {
    const columnsArray = [
      // {
      //   id: 'code',
      //   header: t('ref_no'),
      //   accessorKey: 'code',
      //   sort: true,
      //   visibilityLock: false,
      //   cell: ({ cell }: any) => {
      //     return (
      //       <Link className="text-primary clickable-text-primary" href={`${opId !== '' ? `/crm/a/tasks/${cell.id}?f=op&opId=${opId}` : `/crm/a/tasks/${cell.id}`}`}>
      //         {cell.code}
      //       </Link>
      //     );
      //   },
      // },
      {
        id: 'task',
        header: t('task'),
        accessorKey: 'task',
        sort: true,
        visibilityLock: false,
        size: '15rem',
      },
      {
        id: 'opportunity',
        header: t('lead'),
        accessorKey: 'opportunity',
        cell: ({ cell, onClick }: { cell: any; onClick: Function }) => (
          <div className="text text-nowrap" onClick={() => onClick()}>
            <OpportunityCell {...{ opData, cell }} />
          </div>
        ),
        nowrap: true,
      },
      {
        id: 'opportunity_stage',
        header: t('lead_stage'),
        accessorKey: 'opportunity_stage',
        cell: ({ cell, onClick }: { cell: any; onClick: Function }) => (
          <div className="text" onClick={() => onClick()}>
            <OpportunityStageCell {...{ opData, cell }} />
          </div>
        ),
      },
      {
        id: 'assigned_user_name',
        header: t('assigned_to'),
        accessorKey: 'assigned_user_name',
        sort: true,
      },
      {
        id: 'assigned_date',
        header: t('assigned_date'),
        accessorKey: 'assigned_date',
        sort: true,
        cell: ({ cell }: any) => <span>{formatDate(cell.assigned_date)}</span>,
      },
      {
        id: 'start_date',
        header: t('start_date'),
        accessorKey: 'start_date',
        sort: true,
        cell: ({ cell }: any) => <span>{formatDate(cell.start_date)}</span>,
      },
      {
        id: 'due_date',
        header: t('due_date'),
        accessorKey: 'due_date',
        sort: true,
        cell: ({ cell }: any) => <span>{formatDate(cell.due_date)}</span>,
      },
      {
        id: 'task_status_name',
        header: t('current_status'),
        accessorKey: 'task_status_name',
        sort: true,
        cell: ({ cell }: any) => {
          return (
            <div
              className={`rounded-5 fw-semibold badge d-flex flex-row justify-content-between gap-1 d-inline-flex`}
              style={{ background: hexToRgba(cell.task_status_color, 0.1), border: `1px solid ${hexToRgba(cell.task_status_color, 0.4)}`, color: cell.task_status_color }}
              onClick={(e) => e.stopPropagation()}
            >
              {cell.task_status_name}
              <Dropdown trigger={<Flexicon icon="chevron-down" variant="line" size={12} className="pointer" />}>
                {(onClose: Function) => (
                  <span className="t-action">
                    {taskStatus.map((status) => (
                      <DropdownItem onClick={() => (handleChangeStatus(cell.id, status.id), onClose())} key={status.id}>
                        <span>{status.name}</span>
                      </DropdownItem>
                    ))}
                  </span>
                )}
              </Dropdown>
            </div>
          );
        },
      },
      // {
      //   id: 'description',
      //   header: t('description'),
      //   accessorKey: 'description',
      //   sort: true,
      // },
      {
        header: t('action'),
        align: 'center',
        accessorKey: 'id',
        cell: ({ cell }: { cell: any }) => {
          return (
            <Dropdown
              trigger={
                <span className="action-icon">
                  <Flexicon icon="dots-horizontal" variant="line" size={17} />
                </span>
              }
            >
              {(onClose: Function) => (
                <span className="t-action">
                  <DropdownItem onClick={() => (setIsFullscreen(false), onView(cell.getValue()), onClose())}>
                    <span className="d-flex gap-2">
                      <Flexicon icon="eye" variant="line" size={17} />
                      <span>{t('view')}</span>
                    </span>
                  </DropdownItem>
                  <DropdownItem onClick={() => (setIsFullscreen(false), onEdit(cell.getValue()), onClose())}>
                    <span className="d-flex gap-2">
                      <Flexicon icon="pencil-line" variant="line" size={17} />
                      <span>{t('edit')}</span>
                    </span>
                  </DropdownItem>
                  {cell.task_status_name === 'Todo' && (
                    <DeleteConfirmPop
                      trigger={
                        <DropdownItem onClick={() => null}>
                          <span className="d-flex gap-2 w-100">
                            <Flexicon icon="trash-03" variant="line" size={17} />
                            <span>{t('delete')}</span>
                          </span>
                        </DropdownItem>
                      }
                      deleteId={cell.id}
                      {...{ handleOnDelete, onClose }}
                    />
                  )}
                </span>
              )}
            </Dropdown>
          );
        },
        customizable: false,
      },
    ];

    if (opId !== '') {
      return columnsArray.filter((column) => column.id !== 'opportunity' && column.id !== 'opportunity_stage');
    }

    return columnsArray;
  }, [opData.columnKeyVers]);

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: (props: any) => fetchAllTaskTableData(props, opId),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
      action: (id: string) => router.push(`/crm/a/tasks/${id}?f=op&opId=${opId}`),
    },
    customState: {
      initState: {
        filters: {},
      },
      reducer: (_: any, action: any) => filterReducer({ action, setFilterComKey }),
    },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers, tableVers, tVers]);

  useEffect(() => {
    const fetchOpportunitiesData = async () => {
      const opportunityIdString = convertToString(tableProperties.tableData, 'id');

      if (opportunityIdString) {
        opDispatch({ type: 'set-loader' });
        try {
          const responseData = await getManyOpportunities(opportunityIdString);
          const opporDataMap = convertToMap(responseData.result, 'task_id');

          if (responseData.is_success) {
            opDispatch({ data: opporDataMap, type: 'set-data' });
          }
        } catch (error) {
          console.log(error);
        }
      }
    };

    fetchOpportunitiesData();
  }, [tableProperties.tableData]);

  useEffect(() => {
    const fetchTaskStatus = async () => {
      const response = await getAllTaskStatuses();
      if (response.is_success) {
        setTaskStatus(response.result);
      }
    };
    fetchTaskStatus();
  }, [tableColumnVers, tableVers, tVers]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
        <Table heading={<PageHeading title={t('task_management')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible, setIsFilterVisible }} />
      </div>
      <CustomizeColumn
        key={tableColumnVers}
        isOpen={isCustColumnVisible}
        tableName={tableName}
        columns={tableColumns}
        onClose={() => setIsCustColumnVisible(false)}
        afterUpdate={() => setTableColumnVers((prevTableColumnVers) => prevTableColumnVers + 1)}
      />
      <TaskFilter
        {...{ opId }}
        key={`filter-${filterComKey}`}
        isOpen={isFilterVisible}
        onClose={() => setIsFilterVisible(false)}
        onSubmit={(filterData: any, isReset: boolean) => (setIsFilterVisible(false), tableProperties.tableDispatch({ filterData, isReset }))}
      />
    </>
  );
}

export default AssignedTasksList;

export const OpportunityCell = ({ opData, cell }: { opData: any; cell: any }) => {
  if (opData.loadingState && cell.id) {
    return <Skeleton height="20px" />;
  }

  const opportunity = opData?.data[cell.id] || null;

  if (opportunity) {
    return (
      <div>
        <div className="text-muted fs-12">{opportunity.opportunity_code}</div>
        <div>{opportunity.opportunity_title}</div>
      </div>
    );
  }

  return null;
};

export const OpportunityStageCell = ({ opData, cell }: { opData: any; cell: any }) => {
  if (opData.loadingState && cell.id) {
    return <Skeleton height="20px" />;
  }

  const opportunity = opData?.data[cell.id] || null;

  if (opportunity) {
    return (
      <div
        className={`rounded-5 fw-semibold badge`}
        style={{ background: hexToRgba(opportunity.stage_color, 0.1), border: `1px solid ${hexToRgba(opportunity.stage_color, 0.4)}`, color: opportunity.stage_color }}
      >
        {opportunity.stage_name}
      </div>
    );
  }

  return null;
};
