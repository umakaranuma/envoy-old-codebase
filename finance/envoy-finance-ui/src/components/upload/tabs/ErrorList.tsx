import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { UploadSummaryData } from '@/interface/model';
import { useAsyncTable } from '@apptimus-ui/table';
import { useMemo } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';

interface ErrorListProps {
  data?: UploadSummaryData;
}

function ErrorList({ data }: ErrorListProps) {
  const t = useTrans('label.invoice,otr.common');

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      // {
      //   id: 'row_id',
      //   header: t('row_id'),
      //   accessorKey: 'row_id',
      //   sort: true,
      //   visibilityLock: false,
      // },
      // {
      //   id: 'invoice_number',
      //   header: t('invoice_number'),
      //   accessorKey: 'invoice_number',
      //   sort: true,
      // },
      // {
      //   id: 'insurer_invoice_id',
      //   header: t('insurer_invoice_id'),
      //   accessorKey: 'insurer_invoice_id',
      //   sort: true,
      // },
      {
        id: 'status',
        header: t('status'),
        accessorKey: 'status',
        sort: true,
        cell: ({ cell }: { cell: any }) => {
          const status = cell.status;
          let badgeClass = 'bg-info';

          switch (status) {
            case 'created':
              badgeClass = 'bg-success';
              break;
            case 'updated':
              badgeClass = 'bg-info';
              break;
            case 'error':
              badgeClass = 'bg-danger';
              break;
            case 'ignored':
              badgeClass = 'bg-warning';
              break;
          }

          return <span className={`badge ${badgeClass}`}>{t(status)}</span>;
        },
      },
      {
        id: 'details',
        header: t('details'),
        accessorKey: 'details',
        sort: true,
        cell: ({ cell }: { cell: any }) => {
          const details = cell.details || cell;
          if (details.error) {
            return <div className="text-danger">{details.error}</div>;
          }
          if (details.ignored) {
            return <div className="text-warning">{details.ignored}</div>;
          }
          if (details.created) {
            return <div className="text-success">{details.created}</div>;
          }
          return <span className="text-muted">-</span>;
        },
      },
    ],
    [t],
  );

  const tableData = useMemo(() => {
    if (!data?.result?.results) return [];
    return data.result.results;
  }, [data]);

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: () => Promise.resolve({ data: tableData, total: tableData.length }),
    paginate: true,
    rowSelection: false,
  });

  return (
    <>
      <div className={`data-table-container card custom-card`}>
        <Table {...{ tableProperties, recordControl: false, searchOption: false }} />
      </div>
    </>
  );
}

export default ErrorList;
