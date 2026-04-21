import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchAllTypes } from '../services';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import ProductCategoriesFilter from './ProductCategoriesFilter';
import Link from 'next/link';

function ProductCategoriesList({ tableVers, onView, onEdit, handleOnDelete }: { tableVers: number; onView: Function; onEdit: Function; onDelete: Function; handleOnDelete: Function }) {
  const t = useTrans('label.product_categories,otr.common');
  const tableName = 'product_categories';
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [isFilterVisible, setIsFilterVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const [filterComKey, setFilterComKey] = useState(0);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'title',
        header: t('name'),
        accessorKey: 'title',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: any) => {
          return (
            <Link className="text-primary clickable-text-primary" href={`/a/product-categories/${cell.id}?t=basic`}>
              {cell.title}
            </Link>
          );
        },
      },
      {
        id: 'description',
        header: t('description'),
        accessorKey: 'description',
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
                {/* <DropdownItem onClick={() => (setIsFullscreen(false), onDelete(cell.getValue()), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="trash-03" variant="line" size={17} />
                    <span>{t('delete')}</span>
                  </span>
                </DropdownItem> */}
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
    loadData: fetchAllTypes,
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
  }, [tableColumnVers, tableVers]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
        <Table heading={<PageHeading title={t('product_categories')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible }} />
      </div>
      <CustomizeColumn
        key={tableColumnVers}
        isOpen={isCustColumnVisible}
        tableName={tableName}
        columns={tableColumns}
        onClose={() => setIsCustColumnVisible(false)}
        afterUpdate={() => setTableColumnVers((prevTableColumnVers) => prevTableColumnVers + 1)}
      />
      <ProductCategoriesFilter
        key={`filter-${filterComKey}`}
        isOpen={isFilterVisible}
        onClose={() => setIsFilterVisible(false)}
        onSubmit={(filterData: any, isReset: boolean) => (setIsFilterVisible(false), tableProperties.tableDispatch({ filterData, isReset }))}
      />
    </>
  );
}

export default ProductCategoriesList;
