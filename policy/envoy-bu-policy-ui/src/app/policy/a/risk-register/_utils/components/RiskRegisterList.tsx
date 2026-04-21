import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchRiskTableData } from '../services';
import { formatDate, thousandSeparator } from '@/helpers/services/commonService';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import { deleteRisk } from '../api-service';
import { toaster } from '@/helpers/services/toaster';
import { getCurrency } from '@/helpers/services/currencyService';

function RiskRegisterList({ onView, onEdit }: { onView: Function; onEdit: Function }) {
  const t = useTrans('label.risk_register,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const tableName = 'risk-register-list';
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const [_filterComKey, setFilterComKey] = useState(0);
  const currency = getCurrency();

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteRisk(deleteId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      onClose();
      setTableColumnVers((prev) => prev + 1);
    }
  };

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'code',
        header: t('risk_id'),
        accessorKey: 'code',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'customer_name',
        header: t('account'),
        accessorKey: 'customer_name',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'risk_type_title',
        header: t('risk_type'),
        accessorKey: 'risk_type_title',
        sort: true,
        visibilityLock: false,
      },
      // {
      //   id: 'policy_request_id',
      //   header: t('policy_number'),
      //   accessorKey: 'policy_request_id',
      //   sort: true,
      // },
      {
        id: 'intimation_time',
        header: t('registered_date'),
        accessorKey: 'created_at',
        sort: true,
        align: 'center',
        cell: ({ cell }: { cell: any }) => <span>{formatDate(cell.created_at) || ''}</span>,
      },
      {
        id: 'sum_insured',
        header: `${t('sum_insured')} (${currency.code})`,
        accessorKey: 'sum_insured',
        sort: true,
        visibilityLock: false,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.policy_base?.sum_insured) || '-'}</div>,
      },
      // {
      //   id: 'policy_status_name',
      //   header: t('policy_status'),
      //   accessorKey: 'policy_status_name',
      //   sort: true,
      //   cell: ({ cell, onClick }: any) => {
      //     return (
      //       <div
      //         className={`rounded-5 fw-semibold badge`}
      //         style={{
      //           background: hexToRgba(cell.policy_status_color ? cell.policy_status_color : '', 0.1),
      //           border: `1px solid ${hexToRgba(cell.policy_status_color ? cell.policy_status_color : '', 0.4)}`,
      //           color: cell.policy_status_color ? cell.policy_status_color : '',
      //         }}
      //         onClick={onClick}
      //       >
      //         {cell.policy_status_name}
      //       </div>
      //     );
      //   },
      // },
      // {
      //   id: 'intimation_time',
      //   header: t('recommendation_document'),
      //   accessorKey: 'created_at',
      //   sort: true,
      //   align: 'center',
      //   cell: ({ cell }: { cell: any }) => <span>{formatDate(cell.created_at) || ''}</span>,
      // },
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
                <DropdownItem onClick={() => (setIsFullscreen(false), onView(cell.getValue()), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="eye" variant="line" size={17} />
                    <span>{t('view')}</span>
                  </span>
                </DropdownItem>
                <DropdownItem onClick={() => (setIsFullscreen(false), onEdit(cell.getValue()), onClose())}>
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
                  deleteId={cell.id}
                  {...{ handleOnDelete, onClose }}
                />
              </span>
            )}
          </Dropdown>
        ),
        customizable: false,
      },
    ],
    [],
  );

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const reducer = (_state: any, action: any) => {
    if (action.isReset) {
      setFilterComKey((prevFilterComKey) => prevFilterComKey + 1);
    }

    return {
      filters: action.filterData,
    };
  };

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: (props: any) => fetchRiskTableData(props),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
      action: (selectedId: string) => onView(selectedId),
    },
    customState: {
      initState: {
        filters: {},
      },
      reducer: reducer,
    },
  });

  useEffect(() => {
    tableProperties.reload();
    // tableProperties.reset({ type: 'row-selection' });
  }, [tableColumnVers]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
        <Table heading={<PageHeading title={t('risk_register')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible }} />
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

export default RiskRegisterList;
