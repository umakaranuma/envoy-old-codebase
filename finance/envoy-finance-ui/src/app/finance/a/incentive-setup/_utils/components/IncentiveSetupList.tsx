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
import { fetchAllIncentiveSetupData } from '../services';
import { formatDate, snakeToTitleCase, thousandSeparator } from '@/helpers/services/commonService';
import { getCurrency } from '@/helpers/services/currencyService';

function IncentiveSetupList({ tableVers, onView, handleOnDelete, onEdit }: { tableVers: number; onView: Function; handleOnDelete: Function; onEdit: Function }) {
  const t = useTrans('label.incentive_setup,otr.common');
  const tableName = 'commission_setup';
  const currency = getCurrency();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'incentive_code',
        header: t('code'),
        accessorKey: 'incentive_code',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'name',
        header: t('name'),
        accessorKey: 'name',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'description',
        header: t('description'),
        accessorKey: 'description',
        sort: true,
        cell: ({ cell }: { cell: any }) => (
          <div className="text-truncate" style={{ maxWidth: '100px' }}>
            {cell.getValue() || '-'}
          </div>
        ),
      },
      {
        id: 'start_date',
        header: t('start_date'),
        accessorKey: 'start_date',
        sort: true,
        cell: ({ cell }: { cell: any }) => <>{formatDate(cell.getValue()) || '-'}</>,
      },
      {
        id: 'end_date',
        header: t('end_date'),
        accessorKey: 'end_date',
        sort: true,
        cell: ({ cell }: { cell: any }) => <>{formatDate(cell.getValue()) || '-'}</>,
      },
      {
        id: 'repeation_type',
        header: t('repeation_type'),
        accessorKey: 'repeation_type',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'reward_type',
        header: t('reward_type'),
        accessorKey: 'reward_type',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'reward_type_value',
        header: `${t('reward_type_value')} (${currency.code})`,
        accessorKey: 'reward_type_value',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'incentive_base_field',
        header: t('incentive_base_field'),
        accessorKey: 'incentive_base_field',
        sort: true,
        cell: ({ cell }: { cell: any }) => {
          return snakeToTitleCase(cell.getValue()) || '-';
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
    loadData: fetchAllIncentiveSetupData,
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

export default IncentiveSetupList;
