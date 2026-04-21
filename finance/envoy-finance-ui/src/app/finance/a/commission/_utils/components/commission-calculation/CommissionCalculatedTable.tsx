import { useAsyncTable } from '@apptimus-ui/table';
import React, { useEffect, useMemo } from 'react';
import { fetchMultiBrokerageRevenuesTableData } from '../../services';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useTrans } from '@/helpers/services/lang/langService';
import Table from '@/components/table-properties/Table';
import { getCurrency } from '@/helpers/services/currencyService';
import { thousandSeparator } from '@/helpers/services/commonService';

function CommissionCalculatedTable({ formData, tableVers }: { formData: any; tableVers: number }) {
  const t = useTrans('label.commission,otr.common');
  const currency = getCurrency();
  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'insurer_name',
        header: t('insurer_name'),
        accessorKey: 'insurer_name',
        sort: true,
      },
      {
        id: 'brokerage_policy_id',
        header: t('total_policies'),
        accessorKey: 'brokerage_policy_id',
        sort: true,
      },
      {
        id: 'insurer_name',
        header: t('insured_details'),
        accessorKey: 'insurer_name',
        sort: true,
      },
      {
        id: 'brokerage_revenue_realized',
        header: `${t('revenue_recognized')} (${currency.code})`,
        accessorKey: 'brokerage_revenue_realized',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'brokerage_revenue_recognized',
        header: `${t('total_revenue_realized')} (${currency.code})`,
        accessorKey: 'brokerage_revenue_recognized',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (params) =>
      fetchMultiBrokerageRevenuesTableData({
        ...params,
        itemsPerPage: 5,
        insurer_id: formData.insurerIds,
        start_date: formData.startDate,
        end_date: formData.endDate,
        data: {
          insurer_ids: formData.insurerIds ? [formData.insurerIds] : [],
        },
      }),
    paginate: true,
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableVers]);

  return (
    <div className={`data-table-container card custom-card`}>
      <div className="fw-bold py-3">{t('commission_calculated')}</div>
      <Table tableProperties={{ ...tableProperties, itemsPerPage: 5 }} searchOption={false} />
    </div>
  );
}

export default CommissionCalculatedTable;
