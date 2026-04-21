import { IElement } from '@/app/a/templates/_utils/model';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo } from 'react';
import { fetchOneRiskTypeTableData } from '../../service';

function RiskTypeList({ riskTypeId, customerId, tableElements, approvalId }: { riskTypeId: string; customerId: string; tableElements: IElement[]; approvalId?: string }) {
  const columns = useMemo<ITablePropertyColumn[]>(() => {
    const columns: ITablePropertyColumn[] = [];

    tableElements?.forEach((element: IElement) => {
      columns.push({
        id: element.id.toString(),
        header: element.label,
        accessorKey: element.id.toString(),
        visibilityLock: false,
      });
    });

    return tableElements.length > 0 ? columns : [];
  }, []);

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchOneRiskTypeTableData(props, riskTypeId, customerId, approvalId),
    paginate: true,
    rowSelection: false,
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableElements]);

  return <Table searchOption={false} isRowPerPageVisible={false} isPaginationTextVisible={false} {...{ tableProperties }} recordControl={false} />;
}

export default RiskTypeList;
