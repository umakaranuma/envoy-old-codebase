import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import { fetchInsurerProductsTableData } from '../../services';

function InsurerProductList({ tableVers, onView, handleOnDelete }: { tableVers: number; onView: Function; handleOnDelete: Function }) {
  const t = useTrans('label.products,otr.common');
  const tableName = 'products';
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'name',
        header: t('product_code'),
        accessorKey: 'code',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'insurer',
        header: t('insurer_name'),
        accessorKey: 'insurer',
        sort: true,
        cell: ({ cell }: { cell: any }) => (
          <div className="text-truncate" style={{ maxWidth: '200px' }}>
            {cell.insurer}
          </div>
        ),
      },
      {
        id: 'name',
        header: t('insurer_product_name'),
        accessorKey: 'name',
        sort: true,
        cell: ({ cell }: { cell: any }) => (
          <div className="text-truncate" style={{ maxWidth: '200px' }}>
            {cell.name}
          </div>
        ),
      },
      {
        id: 'type',
        header: t('risk_type'),
        accessorKey: 'type',
        sort: true,
      },
      {
        id: 'coverage_level',
        header: t('coverage_level'),
        accessorKey: 'coverage_level',
        sort: true,
      },
      {
        id: 'description',
        header: t('description'),
        accessorKey: 'description',
        sort: true,
        cell: ({ cell }: { cell: any }) => (
          <div className="text-truncate" style={{ maxWidth: '200px' }}>
            {cell.description}
          </div>
        ),
      },
      // {
      //   id: 'coverage_details',
      //   header: t('coverage_details'),
      //   accessorKey: 'coverage_details',
      //   sort: true,
      // },
      {
        id: 'currency',
        header: t('currency'),
        accessorKey: 'currency',
        sort: true,
      },
      // {
      //   id: 'premium_amount',
      //   header: t('premium_amount'),
      //   accessorKey: 'premium_amount',
      //   sort: true,
      // },
      // {
      //   id: 'deductible_amount',
      //   header: t('deductible_amount'),
      //   accessorKey: 'deductible_amount',
      //   sort: true,
      // },
      // {
      //   id: 'claim_limit',
      //   header: t('claim_limit'),
      //   accessorKey: 'claim_amount',
      //   sort: true,
      // },
      {
        id: 'last_updated_date',
        header: t('last_updated_date'),
        accessorKey: 'date',
        sort: true,
      },
      {
        id: 'remarks',
        header: t('remarks'),
        accessorKey: 'remarks',
        sort: true,
        cell: ({ cell }: { cell: any }) => (
          <div className="text-truncate" style={{ maxWidth: '200px' }}>
            {cell.remarks}
          </div>
        ),
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
    loadData: (props: any) => fetchInsurerProductsTableData(props),
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
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-2'}`}>
        <Table heading={<PageHeading title={t('products_management')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible }} />
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

export default InsurerProductList;
