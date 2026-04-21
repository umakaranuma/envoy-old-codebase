import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo } from 'react';
import { IElement } from '@/components/others/common/form/template-modal';
import { fetchOneRiskTypeTableData } from '@/app/policy/a/policy-request/_utils/services';

function RiskTypeList({
  riskTypeId,
  customerId,
  tableElements,
  selectedRiskInfoIds,
  policyBaseId,
}: {
  riskTypeId: string;
  customerId: string;
  tableElements: IElement[];
  selectedRiskInfoIds: (id: number[]) => void;
  policyBaseId: string;
}) {
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
    loadData: (props: any) => fetchOneRiskTypeTableData(props, riskTypeId, customerId, '', policyBaseId),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'submission_id',
      mode: 'multiple',
      actionColumn: true,
      enableSelectAll: true,
      action: (value: any, _data: any) => {
        selectedRiskInfoIds(value);
      },
    },
  });

  useEffect(() => {
    tableProperties.reload();
    tableProperties.reset({ type: 'row-selection' });
  }, [tableElements]);

  return <Table searchOption={false} isRowPerPageVisible={false} isPaginationTextVisible={false} isPaginationButtonVisible={false} {...{ tableProperties }} />;
}

export default RiskTypeList;
