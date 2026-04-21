import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchAccTapTableData } from '../../services';

function Interactions({ viewId, curentTap }: { viewId: string; curentTap: string }) {
  const t = useTrans('label.accounts,otr.common');
  const [isFullscreen, setIsFullscreen] = useState(false);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'date',
        header: t('date'),
        accessorKey: 'date',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
      },
      {
        id: 'contact_name',
        header: t('contact_name'),
        accessorKey: 'contact_name',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
      },
      {
        id: 'contact_email',
        header: t('contact_email'),
        accessorKey: 'contact_email',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
      },
      {
        id: 'contact_by_name',
        header: t('contact_by_name'),
        accessorKey: 'contact_by_name',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
      },
      {
        id: 'notes',
        header: t('notes'),
        accessorKey: 'notes',
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
        <Table heading={<PageHeading title={t('interactions')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen }} />
      </div>
    </>
  );
}

export default Interactions;
