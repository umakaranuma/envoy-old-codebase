import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo } from 'react';
import { IElements } from '../../../../model';
import { fetchRiskInfoTableData } from '../../../../services';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';

function RiskTypeList({
  riskTypeId,
  leadId,
  tableVers,
  tableElements,
  onEdit,
  handleOnDelete,
}: {
  riskTypeId: string;
  leadId: string;
  tableVers: number;
  tableElements: IElements[];
  onEdit: (submissionId: string) => void;
  handleOnDelete: Function;
}) {
  const t = useTrans('label.sales_managements,otr.common');

  const columns = useMemo<ITablePropertyColumn[]>(() => {
    // Assert each attribute properly typed
    const baseColumns: ITablePropertyColumn[] = tableElements.map((element: IElements) => ({
      id: element.id.toString(),
      header: element.label,
      accessorKey: element.id.toString(),
      visibilityLock: false,
    }));

    const actionColumn: any = {
      id: 'action',
      header: t('action'),
      accessorKey: 'submission_id',
      cell: ({ cell }: { cell: any }) => (
        <Dropdown
          trigger={
            <span className="action-icon">
              <Flexicon icon="dots-horizontal" variant="line" size={17} />
            </span>
          }
        >
          {(onClose: Function) => (
            <span className="t-action">
              <DropdownItem
                onClick={() => {
                  onEdit(cell.risk_detail_id);
                  onClose();
                }}
              >
                <span className="d-flex gap-2">
                  <Flexicon icon="pencil-line" variant="line" size={17} />
                  {t('edit')}
                </span>
              </DropdownItem>
              <DeleteConfirmPop
                trigger={
                  <DropdownItem onClick={() => null}>
                    <span className="d-flex gap-2 w-100">
                      <Flexicon icon="trash-03" variant="line" size={17} />
                      <span>{t('delete')}</span>
                    </span>
                  </DropdownItem>
                }
                deleteId={cell.risk_detail_id}
                {...{ handleOnDelete, onClose }}
              />
            </span>
          )}
        </Dropdown>
      ),
      customizable: false,
    };

    return [...baseColumns, actionColumn];
  }, [tableElements]);

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchRiskInfoTableData(props, riskTypeId, leadId),
    paginate: true,
    rowSelection: false,
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableElements, tableVers]);

  return (
    <div className={`overflow-hidden px-1 pt-3 rounded-top-0`}>
      <Table searchOption={false} isRowPerPageVisible={false} isPaginationTextVisible={false} isPaginationButtonVisible={false} {...{ tableProperties }} />;
    </div>
  );
}

export default RiskTypeList;
