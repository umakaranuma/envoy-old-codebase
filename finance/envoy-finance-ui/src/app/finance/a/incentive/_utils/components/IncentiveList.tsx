import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import PageHeading from '@/components/others/PageHeading';
import Table from '@/components/table-properties/Table';
import { useTrans } from '@/helpers/services/lang/langService';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import React, { useEffect, useMemo, useState } from 'react';
import { fetchAllIncentiveData } from '../services';
import { formatDate, thousandSeparator } from '@/helpers/services/commonService';
import { getCurrency } from '@/helpers/services/currencyService';

function IncentiveList({ tableVers, onView }: { tableVers: number; onView: Function }) {
  const t = useTrans('label.incentive,otr.common');
  const tableName = 'incentive';
  const currency = getCurrency();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      // {
      //   id: 'id',
      //   header: t('id'),
      //   accessorKey: 'id',
      //   visibilityLock: true,
      //   sort: true,
      //   cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      // },
      {
        id: 'agent_name',
        header: t('name'),
        accessorKey: 'agent_name',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'incentive_setup_name',
        header: t('incentive_setup_name'),
        accessorKey: 'incentive_setup_name',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'commission_date',
        header: t('commission_date'),
        accessorKey: 'commission_date',
        sort: true,
        cell: ({ cell }: { cell: any }) => <>{formatDate(cell.getValue()) || '-'}</>,
      },
      {
        id: 'repetition_type',
        header: t('repetition_type'),
        accessorKey: 'repetition_type',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      // {
      //   id: 'reward_type_name',
      //   header: t('reward_type'),
      //   accessorKey: 'reward_type_name',
      //   sort: true,
      //   cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      // },
      // {
      //   id: 'performance_metric_value',
      //   header: t('performance_metric'),
      //   accessorKey: 'performance_metric_value',
      //   sort: true,
      //   cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      // },
      // {
      //   id: 'actual_performance_value',
      //   header: t('actual_performance'),
      //   accessorKey: 'actual_performance_value',
      //   sort: true,
      //   cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      // },
      {
        id: 'incentive_amount',
        header: `${t('incentive_amount')} (${currency.code})`,
        accessorKey: 'incentive_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'status',
        header: t('status'),
        accessorKey: 'status',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'notes',
        header: t('notes'),
        accessorKey: 'notes',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
    ],
    [t],
  );

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: fetchAllIncentiveData,
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
      enableSelectAll: true,
      action: (selectedId: string) => onView(selectedId),
    },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers, tableVers]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
        <Table heading={<PageHeading title={t('incentive')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible }} />
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

export default IncentiveList;
