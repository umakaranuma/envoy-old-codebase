import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import { fetchAllTypeForms } from '../../services';
import { Button } from '@apptimus-ui/ui-element';

function FormsList({
  tableVers,
  onView,
  handleOnDelete,
  typeId,
  setIsCreateOpen,
}: {
  tableVers: number;
  onView: Function;
  onEdit: Function;
  handleOnDelete: Function;
  typeId: string;
  setIsCreateOpen: Function;
}) {
  const t = useTrans('label.product_categories,otr.common');
  const [tableColumnVers] = useState(0);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'title',
        header: t('title'),
        accessorKey: 'title',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'form',
        header: t('form'),
        accessorKey: 'form',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'data_gethering_type',
        header: t('data_gethering_type'),
        accessorKey: 'data_gethering_type',
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
                {/* <DropdownItem onClick={() => (setIsFullscreen(false), onView(cell.getValue()), onClose())}>
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

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchAllTypeForms(props, typeId),
    paginate: true,
    rowSelection: false,
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
    <div className="bg-white rounded-2 rounded-top-0">
      <div className={`data-table-container card custom-card px-4`}>
        <div className="d-flex justify-content-between align-items-center mb-3 mt-2">
          <div className="datatable-search">{tableProperties.SearchInput as React.ReactNode}</div>
          <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setIsCreateOpen(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('add_new_entity', { entity: t('form') })}</span>
          </Button>
        </div>
        <Table heading={<PageHeading title={t('form')} icon="sun-light" />} searchOption={false} {...{ tableProperties }} />
      </div>
    </div>
  );
}

export default FormsList;
