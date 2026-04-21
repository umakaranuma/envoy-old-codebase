import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchBrokerageRevenuesTableData } from '../services';
import { thousandSeparator } from '@/helpers/services/commonService';
import { getCurrency } from '@/helpers/services/currencyService';

function BrokerageRevenuesList({ tableVers, onView }: { tableVers: number; onView: Function; onEdit: Function; handleOnDelete: Function }) {
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
      //   id: 'insurer_name',
      //   header: t('insurer_info'),
      //   accessorKey: 'insurer_name',
      //   sort: true,
      //   visibilityLock: false,
      // },
      {
        id: 'invoice_number',
        header: t('dr_cr_note_number'),
        accessorKey: 'invoice_number',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
        visibilityLock: false,
      },
      // {
      //   id: 'last_paid_date',
      //   header: t('invoice_date'),
      //   accessorKey: 'last_paid_date',
      //   sort: true,
      // },
      {
        id: 'brokerage_policy_id',
        header: t('policy_info'),
        accessorKey: 'brokerage_policy_id',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      // {
      //   id: 'endorsementI_id',
      //   header: t('endorsementI_id'),
      //   accessorKey: 'endorsementI_id',
      //   sort: true,
      // },
      // {
      //   id: 'insurer_policy_number',
      //   header: t('insurer_policy_number'),
      //   accessorKey: 'insurer_policy_number',
      //   sort: true,
      // },
      // {
      //   id: 'invoice_payment_type',
      //   header: t('invoice_payment_type'),
      //   accessorKey: 'invoice_payment_type',
      //   sort: true,
      // },
      {
        id: 'insurer_name',
        header: t('insurer_info'),
        accessorKey: 'insurer_name',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'brokerage_revenue_percent',
        header: t('brokerage_revenue_persentage'),
        accessorKey: 'brokerage_revenue_percent',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => {
          if (cell.brokerage_revenue_type === 'percentage') {
            return <div className="amount-container">{cell.getValue()} %</div>;
          } else {
            return <div className="amount-container">{`${currency.code} ${thousandSeparator(cell.getValue())}`}</div>;
          }
        },
      },
      {
        id: 'invoice_amount',
        header: `${t('amount')} (${currency.code})`,
        accessorKey: 'invoice_amount',
        align: 'right',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'revenue_recognized',
        header: `${t('revenue_recognized')} (${currency.code})`,
        accessorKey: 'revenue_recognized',
        align: 'right',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'revenue_realized',
        header: `${t('revenue_realized')} (${currency.code})`,
        accessorKey: 'revenue_realized',
        align: 'right',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'outstanding',
        header: `${t('outstanding_amount')} (${currency.code})`,
        accessorKey: 'outstanding',
        align: 'right',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'commission_deductible',
        header: `${t('commission_deductible')} (${currency.code})`,
        accessorKey: 'commission_deductible',
        align: 'right',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      // {
      //   id: 'account_manager',
      //   header: t('account_manager'),
      //   accessorKey: 'account_manager',
      //   sort: true,
      // },
      // {
      //   id: 'credit_period_days',
      //   header: t('credit_period_days'),
      //   accessorKey: 'credit_period_days',
      //   sort: true,
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
    loadData: fetchBrokerageRevenuesTableData,
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
        <Table heading={<PageHeading title={t('brokerage_revenue')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible }} />
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

export default BrokerageRevenuesList;
