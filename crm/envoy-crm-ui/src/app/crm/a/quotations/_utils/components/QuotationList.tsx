'use client';
import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchQuotationTableData } from '../service';
import { formatDate, hexToRgba } from '@/helpers/services/commonService';
import QuotationFilter from './QuotationFilter';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';

function QuotationList({ tableVers, onView, handleOnDelete }: { tableVers: number; onView: Function; handleOnDelete: Function }) {
  const t = useTrans('label.quotations,otr.common');
  const tableName = 'quotation';
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const [filterComKey, setFilterComKey] = useState(0);
  const [isFilterVisible, setIsFilterVisible] = useState(false);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'code',
        header: t('quotation_request_id'),
        accessorKey: 'code',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'requested_data',
        header: t('requested_date'),
        accessorKey: 'requested_data',
        sort: true,
        cell: ({ cell }: { cell: any }) => <span>{formatDate(cell.requested_data) || ''}</span>,
      },
      {
        id: 'request_type',
        header: t('requested_type'),
        accessorKey: 'request_type',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div className="text-capitalize">{cell.request_type}</div>,
      },
      {
        id: 'status',
        header: t('stage'),
        accessorKey: 'status',
        sort: true,
        visibilityLock: false,
        cell: ({ cell, onClick }: any) => {
          return (
            <div className="d-flex justify-content-between align-items-center gap-3" onClick={onClick}>
              <div
                className={`d-flex flex-row align-items-center text-capitalize gap-1 rounded-1 fs-10 fw-bold badge`}
                style={{ background: hexToRgba(cell.status_color, 0.1), border: `1px solid ${cell.status_color}`, color: `${cell.status_color}` }}
              >
                <svg width="9" height="8" viewBox="0 0 9 8" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="4.375" cy="4" r="3" fill={cell.status_color} />
                </svg>
                {cell.status}
              </div>
            </div>
          );
        },
      },
      {
        id: 'created_by_name',
        header: t('requested_by'),
        accessorKey: 'created_by_name',
        sort: true,
      },
      {
        id: 'customer_name',
        header: t('account'),
        accessorKey: 'customer_name',
        sort: true,
      },
      // {
      //   id: 'notes',
      //   header: t('notes'),
      //   accessorKey: 'notes',
      //   sort: true,
      //   cell: ({ cell }: { cell: any }) => (
      //     <div className="text-truncate" style={{ maxWidth: '100px' }}>
      //       {cell.notes}
      //     </div>
      //   ),
      // },
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
                <DropdownItem onClick={() => (setIsFullscreen(false), onView(cell.getValue()), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="eye" variant="line" size={17} />
                    <span>{t('view')}</span>
                  </span>
                </DropdownItem>
                {/* <DropdownItem onClick={() => (setIsFullscreen(false), onEdit(cell.getValue()), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="pencil-line" variant="line" size={17} />
                    <span>{t('edit')}</span>
                  </span>
                </DropdownItem> */}
                {cell.status === 'CONFIRMED' && (
                  <DeleteConfirmPop
                    msg="revert_confirmation_msg"
                    trigger={
                      <DropdownItem onClick={() => null}>
                        <span className="d-flex gap-2 w-100">
                          <Flexicon icon="reverse-left" variant="line" size={17} />
                          <span>{t('revert')}</span>
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
        ),
        customizable: false,
      },
    ],
    [],
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
    loadData: (props: any) => fetchQuotationTableData(props),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
      action: (id: string) => onView(id),
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
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
        <Table heading={<PageHeading title={t('quotation_management')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible, setIsFilterVisible }} />
      </div>
      <CustomizeColumn
        key={tableColumnVers}
        isOpen={isCustColumnVisible}
        tableName={tableName}
        columns={tableColumns}
        onClose={() => setIsCustColumnVisible(false)}
        afterUpdate={() => setTableColumnVers((prevTableColumnVers) => prevTableColumnVers + 1)}
      />
      <QuotationFilter
        key={`filter-${filterComKey}`}
        isOpen={isFilterVisible}
        onClose={() => setIsFilterVisible(false)}
        onSubmit={(filterData: any, isReset: boolean) => (setIsFilterVisible(false), tableProperties.tableDispatch({ filterData, isReset }))}
      />
    </>
  );
}

export default QuotationList;
