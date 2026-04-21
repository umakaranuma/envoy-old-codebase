import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchAllProductTableData } from '../../../services';
import { useParams } from 'next/navigation';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import { Button } from '@apptimus-ui/ui-element';

function ProductList({ tableVers, handleOnDelete, setCreateFormVisible }: { tableVers: number; handleOnDelete: Function; setCreateFormVisible: Function }) {
  const t = useTrans('label.sales_managements,otr.common');
  const tableName = 'tasks';
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const params = useParams();
  const opportunityId = params.managementId?.toString() || '';

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'product_name',
        header: t('name'),
        accessorKey: 'product_name',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'product_code',
        header: t('code'),
        accessorKey: 'product_code',
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
    loadData: (props: any) => fetchAllProductTableData(props, opportunityId),
    paginate: true,
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers, tableVers]);

  return (
    <>
      <div className={`data-table-container card custom-card px-2`}>
        <div className="d-flex justify-content-between align-items-center mb-3 mt-2">
          <div className="datatable-search">{tableProperties.SearchInput as React.ReactNode}</div>
          <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('add_new')}</span>
          </Button>
        </div>
        <Table heading={<PageHeading title={t('task_management')} icon="sun-light" />} searchOption={false} {...{ tableProperties }} />
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

export default ProductList;
