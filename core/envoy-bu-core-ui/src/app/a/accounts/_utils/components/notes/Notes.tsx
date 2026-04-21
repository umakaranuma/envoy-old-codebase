import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchAccTapTableData } from '../../services';

function Notes({ viewId, curentTap }: { viewId: string; curentTap: string }) {
  const t = useTrans('label.accounts,otr.common');
  const [isFullscreen, setIsFullscreen] = useState(false);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'notes',
        header: t('notes'),
        accessorKey: 'notes',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
      },
      {
        id: 'added_at',
        header: t('date'),
        accessorKey: 'added_at',
        sort: true,
        visibilityLock: false,
        accessorFn: (row: any) => row.added_at.split('T')[0],
      },
      {
        id: 'added_by_name',
        header: t('added_by'),
        accessorKey: 'added_by_name',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
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
        <Table heading={<PageHeading title={t('notes')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen }} />
      </div>
    </>
  );
}

export default Notes;
