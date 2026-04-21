import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchAllSingleAgentCommisonTableData } from '../_utils/services';
import { formatDate, thousandSeparator } from '@/helpers/services/commonService';

function SingleAgentCommisonList({ commisonId }: { commisonId: string }) {
  const t = useTrans('label.commission,otr.common');
  const tableName = 'single_agent_commission';
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'id',
        header: t('payment_id'),
        accessorKey: 'id',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => {
          return <>{'P ' + cell.id}</>;
        },
      },
      {
        id: 'payment_amount',
        header: t('payment_amount'),
        accessorKey: 'payment_amount',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'payment_date',
        header: t('date_of_payment'),
        accessorKey: 'payment_date',
        sort: true,
        cell: ({ cell }: { cell: any }) => formatDate(cell.getValue()),
      },
    ],
    [],
  );

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: (params) => fetchAllSingleAgentCommisonTableData({ ...params, id: commisonId }),
    paginate: true,
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
        <Table heading={<PageHeading title={t('agent_commission')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible }} />
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

export default SingleAgentCommisonList;
