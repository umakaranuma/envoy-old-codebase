import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useMemo } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchErrorTableData } from '../../../service';

function ErrorList({ type }: { type: string }) {
  console.log(type);

  const t = useTrans('label.invoice,otr.common');
  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'record_number',
        header: t('record_number'),
        accessorKey: 'record_number',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'error_description',
        header: t('error_description'),
        accessorKey: 'error_description',
        sort: true,
      },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: fetchErrorTableData,
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
