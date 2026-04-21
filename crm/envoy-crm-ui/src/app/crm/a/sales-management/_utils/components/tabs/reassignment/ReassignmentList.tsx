import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams } from 'next/navigation';
import { fetchAllSalesAgentHistoryTableData } from '../../../services';
import { formatDate } from '@/helpers/services/commonService';

function ReassignmentList() {
  const t = useTrans('label.tasks,otr.common');
  const tableName = 'tasks';
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const params = useParams();
  const leadId = params.managementId?.toString() || '';
  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'from_agent_name',
        header: t('assigned_from'),
        accessorKey: 'from_agent_name',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'to_agent_name',
        header: t('assigned_to'),
        accessorKey: 'to_agent_name',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'changed_by_name',
        header: t('changed_by'),
        accessorKey: 'changed_by_name',
        sort: true,
        // cell: ({ cell }: { cell: any }) => <span>{formatDate(cell.created_at) || ''}</span>,
      },
      {
        id: 'updated_at',
        header: t('updated_on'),
        accessorKey: 'updated_at',
        sort: true,
        cell: ({ cell }: { cell: any }) => <span>{formatDate(cell.updated_at) || ''}</span>,
      },
      // {
      //   id: 'remark',
      //   header: t('remarks'),
      //   accessorKey: 'remark',
      //   sort: true,
      // },
    ],
    [],
  );

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: (props: any) => fetchAllSalesAgentHistoryTableData(props, leadId),
    paginate: true,
    rowSelection: false,
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers]);

  return (
    <>
      <div>
        <Table heading={<PageHeading title={t('interaction')} />} {...{ tableProperties, searchOption: false }} />
      </div>
      <CustomizeColumn
        key={tableColumnVers}
        isOpen={isCustColumnVisible}
        tableName={tableName}
        columns={tableColumns}
        onClose={() => setIsCustColumnVisible(false)}
        afterUpdate={() => setTableColumnVers((prevTableColumnVers) => prevTableColumnVers + 1)}
      />
    </>
  );
}

export default ReassignmentList;
