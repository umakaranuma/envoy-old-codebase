import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchAccTapTableData } from '../../services';

function Leads({ viewId, curentTap }: { viewId: string; curentTap: string }) {
  const t = useTrans('label.accounts,otr.common');
  const [isFullscreen, setIsFullscreen] = useState(false);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'title',
        header: t('title'),
        accessorKey: 'title',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'type',
        header: t('type'),
        accessorKey: 'type',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
      },
      {
        id: 'contact_number',
        header: t('contact_number'),
        accessorKey: 'contact_number',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
      },
      {
        id: 'email',
        header: t('email'),
        accessorKey: 'email',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
      },
      {
        id: 'code',
        header: t('code'),
        accessorKey: 'code',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
      },
      {
        id: 'last_contacted_date',
        header: t('last_contacted_date'),
        accessorKey: 'last_contacted_date',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
      },
      {
        id: 'remarks',
        header: t('remarks'),
        accessorKey: 'remarks',
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
        <Table heading={<PageHeading title={t('leads')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen }} />
      </div>
    </>
  );
}

export default Leads;
