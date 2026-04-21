import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useMemo } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { getCurrency } from '@/helpers/services/currencyService';
import { thousandSeparator } from '@/helpers/services/commonService';
import { fetchOneCommissionHistoryDeductible } from '../../services';
import { useParams } from 'next/navigation';

function DeductibleList() {
  const t = useTrans('label.commission,otr.common');
  const currency = getCurrency();
  const params = useParams();
  const commissionId = params?.comId?.toString() || '';

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      // {
      //   id: 'policy_info',
      //   header: t('policy_info'),
      //   accessorKey: 'policy_info',
      //   sort: true,
      // },
      {
        id: 'insurer_name',
        header: t('insurer_name'),
        accessorKey: 'insurer_name',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'invoice_number',
        header: t('dr_note_number'),
        accessorKey: 'invoice_number',
        sort: true,
      },
      {
        id: 'brokerage_policy_id',
        header: t('policy_id'),
        accessorKey: 'brokerage_policy_id',
        sort: true,
      },
      {
        id: 'revenue_recognized',
        header: `${t('revenue_recognized')} (${currency.code})`,
        accessorKey: 'revenue_recognized',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'revenue_realized',
        header: `${t('revenue_realized')} (${currency.code})`,
        accessorKey: 'revenue_realized',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => {
          return <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>;
        },
      },
      {
        id: 'settlement_amount',
        header: `${t('physical_credit_note_value')} (${currency.code})`,
        accessorKey: 'settlement_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (params) => fetchOneCommissionHistoryDeductible(params, commissionId),
    paginate: true,
    rowSelection: false,
    // rowSelectionProp: {
    //   key: 'id',
    //   mode: 'single',
    //   action: (selectedId: string) => onView(selectedId),
    // },
  });

  return (
    <div className={`data-table-container card custom-card mt-2`}>
      <div className="fw-bold py-3">{t('deductibles')}</div>
      <Table heading={<PageHeading title={t('deductibles')} icon="sun-light" />} {...{ tableProperties, searchOption: false }} />
    </div>
  );
}

export default DeductibleList;
