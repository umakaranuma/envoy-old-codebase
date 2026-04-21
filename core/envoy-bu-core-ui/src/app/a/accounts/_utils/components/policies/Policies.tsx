import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchAccTapTableData } from '../../services';
import { thousandSeparator } from '@/helpers/services/commonService';

function Policies({ viewId, curentTap }: { viewId: string; curentTap: string }) {
  const t = useTrans('label.accounts,otr.common');
  const [isFullscreen, setIsFullscreen] = useState(false);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'brokerage_policy_id',
        header: t('policy_id'),
        accessorKey: 'brokerage_policy_id',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'product_name',
        header: t('product_name'),
        accessorKey: 'product_name',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'policy_start_date',
        header: t('policy_start_date'),
        accessorKey: 'policy_start_date',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'policy_expiry_date',
        header: t('policy_expiry_date'),
        accessorKey: 'policy_expiry_date',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'premium_amount',
        header: t('premium_amount'),
        accessorKey: 'premium_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: async (props: any) => {
      return await fetchAccTapTableData({ ...props, id: viewId, tap: curentTap });
    },
    paginate: true,
  });

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
        <Table heading={<PageHeading title={t('policies')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen }} />
      </div>
    </>
  );
}

export default Policies;
