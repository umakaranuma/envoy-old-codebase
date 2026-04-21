import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import PageHeading from '@/components/others/PageHeading';
import Table from '@/components/table-properties/Table';
import { useTrans } from '@/helpers/services/lang/langService';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useAsyncTable } from '@apptimus-ui/table';
import React, { useEffect, useMemo, useState } from 'react';
import { fetchAllCommissionData } from '../services';
import { thousandSeparator } from '@/helpers/services/commonService';
import { getCurrency } from '@/helpers/services/currencyService';
import ProfileInfo from '@/components/others/page-related/ProfileInfo';

function CommissionSetupList({ tableVers, onView, handleOnDelete, currentTab, onEdit }: { tableVers: number; onView: Function; handleOnDelete: Function; currentTab: string; onEdit: Function }) {
  const t = useTrans('label.commission_setup,otr.common');
  const tableName = 'commission_setup';
  const currency = getCurrency();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'product_name',
        header: t('product_name'),
        accessorKey: 'product_name',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => {
          return <>{cell.product_group_name ? cell.product_group_name : cell.product_name}</>;
        },
      },
      {
        id: 'insurer_name',
        header: t('insurer'),
        accessorKey: 'insurer_name',
        sort: true,
        cell: ({ cell }: { cell: any }) => {
          return cell.insurer ? (
            <ProfileInfo title={cell.insurer?.name || '-'} imageKey={cell.insurer?.logo || ''} subtitle={cell.insurer?.email || '-'} defaultImage="/images/default-profile.png" shape="square" />
          ) : (
            '-'
          );
        },
      },
      {
        id: 'transaction_type_name',
        header: t('transaction_type'),
        accessorKey: 'transaction_type_name',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'brokerage_revenue_percent',
        header: t('brokerage_revenue_persentage'),
        accessorKey: 'brokerage_revenue_percent',
        align: 'right',
        sort: true,
        cell: ({ cell }: { cell: any }) => {
          const value = cell.brokerage_revenue_percent;
          const isPercentage = cell.brokerage_revenue_percent_type !== 'fixed';
          return <div className="amount-container">{isPercentage ? `${value}%` : `${currency.code} ${thousandSeparator(value)}`}</div>;
        },
      },
      {
        id: 'agent_commission_percent',
        header: t('agent_commission_persentage'),
        accessorKey: 'agent_commission_percent',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => {
          const value = cell.agent_commission_percent;
          const isPercentage = cell.agent_commission_percent_type !== 'fixed';
          return <div className="amount-container">{isPercentage ? `${value}%` : `${currency.code} ${thousandSeparator(value)}`}</div>;
        },
      },
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

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: (params) => fetchAllCommissionData({ ...params, tab: currentTab }),
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
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-2'}`}>
        <Table heading={<PageHeading title={t('flags')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible }} />
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

export default CommissionSetupList;
