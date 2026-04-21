import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo } from 'react';
import { IElement } from '@/components/others/common/form/template-modal';
import React from 'react';
import { fetchOneRiskInfoTableData } from './service';

const RiskTypeList = ({ riskTypeId, customerId, tableElements, policyBaseId }: { riskTypeId: string; customerId: string; tableElements: IElement[]; policyBaseId?: string }) => {
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

    return columns;
  }, []);

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchOneRiskInfoTableData(props, riskTypeId, customerId, policyBaseId),
    paginate: true,
    rowSelection: false,
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableElements]);
  return <Table searchOption={false} isRowPerPageVisible={false} isPaginationTextVisible={false} isPaginationButtonVisible={false} {...{ tableProperties }} />;
};

export default RiskTypeList;
