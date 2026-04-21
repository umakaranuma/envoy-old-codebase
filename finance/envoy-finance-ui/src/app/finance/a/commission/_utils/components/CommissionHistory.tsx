import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { getCurrency } from '@/helpers/services/currencyService';
import { formatDate, thousandSeparator } from '@/helpers/services/commonService';
import { fetchCommissionHistoryTableData } from '../services';
import { useRouter } from 'next/navigation';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';

function CommissionHistory() {
  const t = useTrans('label.commission,otr.common');
  const tableName = 'channel';
  const currency = getCurrency();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const [_filterComKey, setFilterComKey] = useState(0);
  const router = useRouter();

  const onView = (id: string) => {
    router.push(`/finance/a/commission/history/${id}`);
  };
  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      // {
      //   id: 'policy_info',
      //   header: t('policy_info'),
      //   accessorKey: 'policy_info',
      //   sort: true,
      // },
      {
        id: 'year',
        header: t('year'),
        accessorKey: 'year',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'period',
        header: t('period'),
        accessorKey: 'period',
        sort: true,
        cell: ({ cell }: { cell: any }) => (
          <div className="text-nowrap">
            {formatDate(cell.period_start)} to {formatDate(cell.period_end)}
          </div>
        ),
      },
      // {
      //   id: 'invoice_status',
      //   header: t('invoice_status'),
      //   accessorKey: 'invoice_status',
      //   sort: true,
      // },
      {
        id: 'processed_date',
        header: t('processed_date'),
        accessorKey: 'processed_date',
        sort: true,
      },
      {
        id: 'gross_revenue',
        header: `${t('gross_revenue')} (${currency.code})`,
        accessorKey: 'gross_revenue',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'total_deductibles',
        header: `${t('total_deductibles')} (${currency.code})`,
        accessorKey: 'total_deductibles',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => {
          // if (cell.agent_commission_type === 'percentage') {
          //   return <div>{cell.getValue()} %</div>;
          // } else {
          return <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>;
          // }
        },
      },
      {
        id: 'net_revenue',
        header: `${t('net_revenue')} (${currency.code})`,
        accessorKey: 'net_revenue',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      // {
      //   id: 'my_commission_percentage',
      //   header: t('my_commission_percentage'),
      //   accessorKey: 'my_commission_percentage',
      //   sort: true,
      // },
      {
        id: 'total_realized_commission',
        header: `${t('total_realized_commission')} (${currency.code})`,
        accessorKey: 'total_realized_commission',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      // {
      //   id: 'outstanding',
      //   header: `${t('outstanding_amount')} (${currency.code})`,
      //   accessorKey: 'outstanding',
      //   sort: true,
      //   align: 'right',
      //   cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      // },
      // {
      //   id: 'status',
      //   header: t('status'),
      //   accessorKey: 'status',
      //   sort: true,
      //   cell: ({ cell, onClick }: any) => (
      //     <div
      //       className="rounded-5 fw-semibold badge"
      //       style={{ background: hexToRgba(cell?.status_color || '', 0.1), border: `1px solid ${cell?.status_color}`, color: cell?.status_color }}
      //       onClick={onClick}
      //     >
      //       {cell?.status}
      //     </div>
      //   ),
      // },
      {
        header: t('action'),
        align: 'center',
        accessorKey: 'commission_id',
        cell: ({ cell }: { cell: any }) => (
          <Dropdown
            trigger={
              <span className="action-icon">
                <Flexicon icon="dots-horizontal" variant="line" size={17} />
              </span>
            }
          >
            {(onClose: Function) => (
              <>
                <DropdownItem onClick={() => (setIsFullscreen(false), onView(cell.getValue()), onClose())}>
                  <span className="d-flex gap-2">
                    <span>{t('view')}</span>
                  </span>
                </DropdownItem>
              </>
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
    loadData: fetchCommissionHistoryTableData,
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'commission_id',
      mode: 'single',
      action: (selectedId: string) => onView(selectedId),
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
  }, [tableColumnVers]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-2'}`}>
        <Table heading={<PageHeading title={t('commission_history')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible }} />
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

export default CommissionHistory;
