import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useMemo } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchPolicyInheritanceTableData } from '../../service';
import { useParams } from 'next/navigation';
import { formatDate } from '@/helpers/services/commonService';

function PolicyInheritanceHistory() {
  const t = useTrans('label.issued_policies,otr.common');
  const params = useParams();
  const policyId = params.policyId?.toString() || '';

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'policy_id',
        header: t('policy_number'),
        accessorKey: 'policy_id',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'created_at',
        header: t('renewed_date'),
        accessorKey: 'created_at',
        sort: true,
        cell: ({ cell }: { cell: any }) => <>{formatDate(cell.created_at)}</>,
      },
      {
        id: 'policy_effective_date',
        header: t('expired_date'),
        accessorKey: 'policy_effective_date',
        sort: true,
        cell: ({ cell }: { cell: any }) => <>{formatDate(cell.policy_effective_date)}</>,
      },
      {
        id: 'created_by',
        header: t('renewed_by'),
        accessorKey: 'created_by',
        sort: true,
      },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchPolicyInheritanceTableData(props, policyId),
    paginate: true,
    rowSelection: true,
  });

  return <Table searchOption={false} isRowPerPageVisible={false} {...{ tableProperties }} />;
}

export default PolicyInheritanceHistory;
