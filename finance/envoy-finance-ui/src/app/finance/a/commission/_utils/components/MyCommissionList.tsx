import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchMyCommissionTableData } from '../services';
import { getCurrency } from '@/helpers/services/currencyService';
import { hexToRgba, thousandSeparator } from '@/helpers/services/commonService';

function MyCommissionList({ tableVers, onView }: { tableVers: number; onView: Function; onEdit: Function; handleOnDelete: Function }) {
  const t = useTrans('label.commission,otr.common');
  const tableName = 'channel';
  const currency = getCurrency();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const [_filterComKey, setFilterComKey] = useState(0);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      // {
      //   id: 'policy_info',
      //   header: t('policy_info'),
      //   accessorKey: 'policy_info',
      //   sort: true,
      // },
      {
        id: 'product_name',
        header: t('product_type'),
        accessorKey: 'product_name',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'invoice_number',
        header: t('dr_cr_note_number'),
        accessorKey: 'invoice_number',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      // {
      //   id: 'invoice_status',
      //   header: t('invoice_status'),
      //   accessorKey: 'invoice_status',
      //   sort: true,
      // },
      // {
      //   id: 'invoice_date',
      //   header: t('invoice_date'),
      //   accessorKey: 'invoice_date',
      //   sort: true,
      // },
      {
        id: 'invoice_amount',
        header: `${t('amount')} (${currency.code})`,
        accessorKey: 'invoice_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'total_agent_commission',
        header: `${t('recognized_commission')} (${currency.code})`,
        accessorKey: 'total_agent_commission',
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
        id: 'revenue_realized',
        header: `${t('realized_commission')} (${currency.code})`,
        accessorKey: 'revenue_realized',
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
        id: 'paid_amount',
        header: `${t('paid_amount')} (${currency.code})`,
        accessorKey: 'paid_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'outstanding',
        header: `${t('outstanding_amount')} (${currency.code})`,
        accessorKey: 'outstanding',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'status',
        header: t('status'),
        accessorKey: 'status',
        sort: true,
        cell: ({ cell, onClick }: any) => (
          <div
            className="rounded-5 fw-semibold badge"
            style={{ background: hexToRgba(cell?.status_color || '', 0.1), border: `1px solid ${cell?.status_color}`, color: cell?.status_color }}
            onClick={onClick}
          >
            {cell?.status}
          </div>
        ),
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
    loadData: fetchMyCommissionTableData,
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
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
  }, [tableColumnVers, tableVers]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-2'}`}>
        <Table heading={<PageHeading title={t('my_commission')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible }} />
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

export default MyCommissionList;
