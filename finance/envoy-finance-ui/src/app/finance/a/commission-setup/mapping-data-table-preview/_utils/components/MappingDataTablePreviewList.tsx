import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import PageHeading from '@/components/others/PageHeading';
import Table from '@/components/table-properties/Table';
import { useTrans } from '@/helpers/services/lang/langService';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useAsyncTable } from '@apptimus-ui/table';
import React, { useEffect, useMemo, useState } from 'react';
import { fetchAllMappingDataTablePreview } from '../services';

function MappingDataTablePreviewList({ tableVers, onView, onEdit }: { tableVers: number; onView: Function; onEdit: Function; handleOnDelete: Function }) {
  const t = useTrans('label.mapping_data_table_preview,otr.common,label.commission_setup');
  const tableName = 'mapping_data_table_preview';
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
      },
      {
        id: 'insurer_info',
        header: t('insurer_info'),
        accessorKey: 'insurer_info',
        sort: true,
      },
      {
        id: 'transaction_type',
        header: t('transaction_type'),
        accessorKey: 'transaction_type',
        sort: true,
      },
      {
        id: 'sales_team',
        header: t('sales_team'),
        accessorKey: 'sales_team',
        sort: true,
      },
      {
        id: 'commission_percentage',
        header: t('commission_percentage'),
        accessorKey: 'commission_percentage',
        sort: true,
      },
      {
        id: 'revised_commission_percentage',
        header: t('revised_commission_percentage'),
        accessorKey: 'revised_commission_percentage',
        sort: true,
      },
      {
        id: 'target_achievements_commission_percentage',
        header: t('target_achievements_commission_percentage'),
        accessorKey: 'target_achievements_commission_percentage',
        sort: true,
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
                <DropdownItem onClick={() => (setIsFullscreen(false), onEdit(cell.getValue()), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="pencil-line" variant="line" size={17} />
                    <span>{t('edit')}</span>
                  </span>
                </DropdownItem>
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
    loadData: fetchAllMappingDataTablePreview,
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
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

export default MappingDataTablePreviewList;
