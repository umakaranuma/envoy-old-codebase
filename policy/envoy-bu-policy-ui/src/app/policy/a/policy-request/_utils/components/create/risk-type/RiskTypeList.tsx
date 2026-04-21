import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import { fetchOneRiskTypeTableData } from '../../../services';
import { IElement } from '@/components/others/common/form/template-modal';
import React from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import { toaster } from '@/helpers/services/toaster';
import { deleteRisk } from '@/app/policy/a/risk-register/_utils/api-service';

const RiskTypeList = ({
  riskTypeId,
  customerId,
  tableVers,
  tableElements,
  selectedRiskIds,
  defaultSelectedRiskIds,
  leadId,
  onEdit,
}: {
  riskTypeId: string;
  customerId: string;
  tableVers: number;
  tableElements: IElement[];
  selectedRiskIds: (ids: any, isTriggered: boolean) => void;
  defaultSelectedRiskIds: any[];
  leadId?: string;
  onEdit: (id: string) => void;
}) => {
  const [defaultRiskId, _setDefaultRiskId] = useState<any[]>(defaultSelectedRiskIds);
  const [isTriggered, setIsTriggered] = useState(false);
  const [tableVersion, setTableVersion] = useState(0);
  const t = useTrans('label.policy_request,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteRisk(deleteId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      onClose();
      setTableVersion((prev) => prev + 1);
    }
  };

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
      ...columns,
      {
        header: t('action'),
        align: 'center',
        accessorKey: 'id',
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
                <DropdownItem onClick={() => (onEdit(cell.risk_id), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="pencil-line" variant="line" size={17} />
                    <span>{t('edit')}</span>
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
                  deleteId={cell.risk_id}
                  {...{ handleOnDelete, onClose }}
                />
              </span>
            )}
          </Dropdown>
        ),
        customizable: false,
      },
    ];
  }, []);

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchOneRiskTypeTableData(props, riskTypeId, customerId, leadId),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'risk_id',
      mode: 'multiple',
      actionColumn: true,
      enableSelectAll: true,
      action: (value: any, _data: any) => {
        console.log('value', value);
        if (!isTriggered) setIsTriggered(true);
        selectedRiskIds(value, isTriggered);
      },
      defaultSelectedKeys: defaultRiskId,
    },
  });

  useEffect(() => {
    tableProperties.reload();
    //tableProperties.reset({ type: 'row-selection' });
  }, [tableElements, tableVers, tableVersion]);

  // if (attributeInit && columns.length === 0) {
  //   return (
  //     <div className="text-center px-5 py-4">
  //       <div className="text-muted panel-title my-2">{t('no_form_config')}</div>
  //       <Link className="text-primary clickable-text fs-14" href={`/a/product-categories/${riskTypeId}?t=forms`}>
  //         {t('configure_it_now')}
  //       </Link>
  //     </div>
  //   );
  // }

  return <Table searchOption={false} isRowPerPageVisible={false} isPaginationTextVisible={false} isPaginationButtonVisible={false} {...{ tableProperties }} />;
};

export default RiskTypeList;
