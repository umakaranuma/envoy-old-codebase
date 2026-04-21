import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchAccTapTableData } from '../../services';
import { useRouter } from 'next/navigation';

function InterestedProducts({ viewId, curentTap }: { viewId: string; curentTap: string }) {
  const t = useTrans('label.accounts,otr.common');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const router = useRouter();
  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'code',
        header: t('code'),
        accessorKey: 'code',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => (
          <div className="clickable-text text-primary" onClick={() => router.push(`/a/products/${cell.id}`)}>
            {cell.id}
          </div>
        ),
      },
      {
        id: 'product_name',
        header: t('name'),
        accessorKey: 'product_name',
        sort: true,
        visibilityLock: false,
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
        <Table heading={<PageHeading title={t('interested_products')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen }} />
      </div>
    </>
  );
}

export default InterestedProducts;
