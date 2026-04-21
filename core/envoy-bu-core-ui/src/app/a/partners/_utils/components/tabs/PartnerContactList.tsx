import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchPartnerContactTableData } from '../../service';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import { Badge } from '@apptimus-ui/ui-element';

function PartnerContactList({
  onEdit,
  handleOnDelete,
  partnerId,
  tableVers,
  setCurrentViewId,
}: {
  onEdit: (id: string) => void;
  handleOnDelete: Function;
  partnerId: string;
  tableVers: any;
  setCurrentViewId: Function;
}) {
  const t = useTrans('label.partners,otr.common');

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      // {
      //   id: 'title',
      //   header: t('salutation'),
      //   accessorKey: 'title',
      //   sort: true,
      //   visibilityLock: false,
      // },
      {
        id: 'name',
        header: t('contact_person_name'),
        accessorKey: 'name',
        sort: true,
      },
      {
        id: 'email',
        header: t('email'),
        accessorKey: 'email',
        sort: true,
      },
      {
        id: 'primary_contact',
        header: t('contact_number'),
        accessorKey: 'primary_contact',
        sort: true,
      },
      {
        id: 'contact_type',
        header: t('contact_type'),
        accessorKey: 'contact_type',
        sort: true,
        cell: ({ cell }: { cell: any }) => <Badge text={cell.getValue()} color={cell.getValue() === 'primary' ? 'primary' : cell.getValue() === 'secondary' ? 'secondary' : 'warning'} radius="pill" />,
      },
      {
        id: 'remarks',
        header: t('remarks'),
        accessorKey: 'remarks',
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
                <DropdownItem onClick={() => (setCurrentViewId(cell.getValue()), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="eye" variant="line" size={17} />
                    <span>{t('view')}</span>
                  </span>
                </DropdownItem>
                <DropdownItem onClick={() => (onEdit(cell.getValue()), onClose())}>
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

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchPartnerContactTableData({ ...props, sp_id: partnerId }),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
      enableSelectAll: true,
      action: (selectedId: string) => {
        setCurrentViewId(selectedId);
      },
    },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableVers]);

  return (
    <>
      <div className={`data-table-container card custom-card mt-4`}>
        <Table {...{ tableProperties, searchOption: false }} />
      </div>
    </>
  );
}

export default PartnerContactList;
