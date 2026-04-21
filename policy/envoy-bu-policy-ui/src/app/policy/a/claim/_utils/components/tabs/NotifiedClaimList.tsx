import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { convertUTCTimeToLocal, formatDate, hexToRgba } from '@/helpers/services/commonService';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import { fetchClaimTableData } from '../../services';
import { changeClaimStatus, getAllCLaimStatus } from '../../api-service';
import { toaster } from '@/helpers/services/toaster';

function NotifiedClaimList({ onView, onEdit, tableVers, selectedIds }: { onView: Function; onEdit: Function; tableVers: number; selectedIds: Function }) {
  const t = useTrans('label.claim,otr.common');
  const tableName = 'polices_requests';
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const [_filterComKey, setFilterComKey] = useState(0);
  // const [isFilterVisible, setIsFilterVisible] = useState(false);
  // const [isFilterVisible, setIsFilterVisible] = useState(false);
  const [statusData, setStatusData] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getAllCLaimStatus();
      responseData?.is_success && setStatusData(responseData.result?.data || []);
    };

    fetchData();
  }, []);

  const changeStatus = async (id: string, statusId: string) => {
    const responseData = await changeClaimStatus({ claim_ids: [id], status_id: statusId });
    if (responseData.is_success) {
      toaster.success(t(responseData.message));
      tableProperties.reload();
    }
  };

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'code',
        header: t('broker_claim_id'),
        accessorKey: 'code',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'insurer_name',
        header: t('insurer_name'),
        accessorKey: 'insurer_name',
        sort: true,
      },
      {
        id: 'customer_name',
        header: t('customer_info'),
        accessorKey: 'customer_name',
        sort: true,
      },
      {
        id: 'intimation_time',
        header: t('broker_intimation_date'),
        accessorKey: 'created_at',
        sort: true,
        visibilityLock: false,
        align: 'center',
        cell: ({ cell }: { cell: any }) => <span>{formatDate(cell.created_at) || ''}</span>,
      },
      {
        id: 'opportunity_type_title',
        header: t('broker_intimation_time'),
        accessorKey: 'name',
        sort: true,
        align: 'center',
        cell: ({ cell }: { cell: any }) => <span>{convertUTCTimeToLocal(cell.created_at, 'time') || ''}</span>,
      },
      // {
      //   id: 'updated_at',
      //   header: t('intimation_date'),
      //   accessorKey: 'updated_at',
      //   sort: true,
      //   align: 'center',
      //   cell: ({ cell }: { cell: any }) => <span>{formatDate(cell.updated_at) || ''}</span>,
      // },
      // {
      //   id: 'nic',
      //   header: t('nic'),
      //   accessorKey: 'nic',
      //   sort: true,
      // },
      {
        id: 'status_name',
        header: t('status'),
        accessorKey: 'status_name',
        sort: true,
        cell: ({ cell }: { cell: any }) => (
          <Dropdown
            trigger={
              <div
                className="rounded-5 fw-semibold badge cursor-pointer"
                style={{
                  background: hexToRgba(cell.status_color ? cell.status_color : '', 0.1),
                  border: `1px solid ${hexToRgba(cell.status_color ? cell.status_color : '', 0.4)}`,
                  color: cell.status_color ? cell.status_color : '',
                }}
              >
                {cell.status_name}
              </div>
            }
          >
            {(onClose: Function) => (
              <span className="t-action">
                {statusData.length > 0 &&
                  statusData.map((status: any) => (
                    <DropdownItem key={status.id} onClick={() => (setIsFullscreen(false), changeStatus(cell.id, status.id), onClose())}>
                      <div
                        className="rounded-5 fw-semibold badge"
                        style={{
                          background: hexToRgba(status.color ? status.color : '', 0.1),
                          border: `1px solid ${hexToRgba(status.color ? status.color : '', 0.4)}`,
                          color: status.color ? status.color : '',
                        }}
                      >
                        {status.name}
                      </div>
                    </DropdownItem>
                  ))}
              </span>
            )}
          </Dropdown>
        ),
      },
      {
        header: t('action'),
        align: 'center',
        accessorKey: 'id',
        cell: ({ cell }: { cell: any }) => (
          <Dropdown
            trigger={
              <span className="action-icon">
                <Flexicon icon="dots-horizontal" variant="line" size={17} />
              </span>
            }
          >
            {(onClose: Function) => (
              <span className="t-action">
                <DropdownItem onClick={() => (setIsFullscreen(false), onView(cell.getValue(), cell.policy_id, cell.template_id), onClose())}>
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
                {/* <DeleteConfirmPop
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
                      /> */}
              </span>
            )}
          </Dropdown>
        ),
        customizable: false,
      },
    ],
    [statusData.length],
  );

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const reducer = (_state: any, action: any) => {
    if (action.isReset) {
      setFilterComKey((prevFilterComKey) => prevFilterComKey + 1);
    }

    return {
      filters: action.filterData,
    };
  };

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: (props: any) => fetchClaimTableData(props, 'claim_notified'),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'multiple',
      actionColumn: true,
      enableSelectAll: true,
      action: (value: any, _data: any) => {
        selectedIds(value);
      },
    },
    customState: {
      initState: {
        filters: {},
      },
      reducer: reducer,
    },
  });

  useEffect(() => {
    tableProperties.reload();
    tableProperties.reset({ type: 'row-selection' });
  }, [tableColumnVers, tableVers]);

  return (
    <>
      <div className={`data-table-container ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : ''}`}>
        <Table heading={<PageHeading title={t('claims')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible }} />
      </div>
      <CustomizeColumn
        key={tableColumnVers}
        isOpen={isCustColumnVisible}
        tableName={tableName}
        columns={tableColumns}
        onClose={() => setIsCustColumnVisible(false)}
        afterUpdate={() => setTableColumnVers((prevTableColumnVers) => prevTableColumnVers + 1)}
      />
    </>
  );
}

export default NotifiedClaimList;
