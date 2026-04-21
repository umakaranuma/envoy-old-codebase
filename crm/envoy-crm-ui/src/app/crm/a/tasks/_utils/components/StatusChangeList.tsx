import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams } from 'next/navigation';
import { fetchAllStatusOfTaskTableData } from '../service';
import { formatDate, hexToRgba } from '@/helpers/services/commonService';

function StatusChangeList() {
  const t = useTrans('label.tasks,otr.common');
  const tableName = 'tasks';
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const params = useParams();
  const taskId = params.taskId?.toString() || '';
  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'progress_stage',
        header: t('status'),
        accessorKey: 'sales_agent_id',
        cell: ({ cell, onClick }: any) => {
          return (
            <div
              className={`rounded-5 fw-semibold badge`}
              style={{ background: hexToRgba(cell.task_status_color || '', 0.1), border: `1px solid ${cell.task_status_color}`, color: cell.task_status_color }}
              onClick={onClick}
            >
              {cell.task_status_name}
            </div>
          );
        },
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'created_at',
        header: t('changed_date'),
        accessorKey: 'created_at',
        sort: true,
        cell: ({ cell }: { cell: any }) => <span>{formatDate(cell.created_at) || ''}</span>,
      },
      {
        id: 'changed_by_name',
        header: t('changed_by'),
        accessorKey: 'changed_by_name',
        sort: true,
      },
      {
        id: 'remark',
        header: t('remarks'),
        accessorKey: 'remark',
        sort: true,
      },
    ],
    [],
  );

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: (props: any) => fetchAllStatusOfTaskTableData(props, taskId),
    paginate: true,
    rowSelection: false,
  });

  return (
    <>
      <div>
        <Table heading={<PageHeading title={t('contacts_management')} icon="sun-light" />} {...{ tableProperties, searchOption: false }} />
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

export default StatusChangeList;
