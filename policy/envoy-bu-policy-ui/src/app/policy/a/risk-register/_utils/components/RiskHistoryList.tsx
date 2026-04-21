import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo } from 'react';
import { IElement } from '@/components/others/common/form/template-modal';
import React from 'react';
import { fetchRiskHistoryTableData } from '../services';
import { useTrans } from '@/helpers/services/lang/langService';

const RiskHistoryList = ({ riskId, tableElements }: { riskId: string; tableElements: IElement[] }) => {
  const t = useTrans('label.risk_register,otr.common');
  const columns = useMemo<ITablePropertyColumn[]>(() => {
    const columns: ITablePropertyColumn[] = [];

    tableElements.forEach((element: IElement) => {
      columns.push({
        id: element.id.toString(),
        header: element.label,
        accessorKey: element.id.toString(),
        visibilityLock: false,
      });
    });

    return [
      {
        id: 'version',
        header: t('version'),
        accessorKey: 'version',
        visibilityLock: false,
      },
      {
        id: 'brokerage_policy_id',
        header: t('policy'),
        accessorKey: 'brokerage_policy_id',
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => <span className="text-nowrap">{cell.getValue() || '-'}</span>,
      },
      {
        id: 'insurer_name',
        header: t('insurer'),
        accessorKey: 'insurer_name',
        visibilityLock: false,
      },
      ...columns,
    ];
  }, []);

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchRiskHistoryTableData(props, riskId),
    paginate: true,
    rowSelection: false,
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableElements]);

  return <Table searchOption={false} isRowPerPageVisible={false} isPaginationTextVisible={false} isPaginationButtonVisible={false} {...{ tableProperties }} />;
};

export default RiskHistoryList;
