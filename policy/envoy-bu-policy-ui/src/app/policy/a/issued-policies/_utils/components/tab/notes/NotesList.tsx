import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchNotesTableData } from '../../../service';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import { formatDate } from '@/helpers/services/commonService';

function NotesList({ tableVers, onView, onEdit, entityId }: { tableVers: number; onView: Function; onEdit: Function; entityId: string }) {
  const t = useTrans('label.issued_policies,otr.common');
  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      // {
      //   id: 'title',
      //   header: t('title'),
      //   accessorKey: 'title',
      //   sort: true,
      //   visibilityLock: false,
      // },
      {
        id: 'notes',
        header: t('content'),
        accessorKey: 'notes',
        sort: true,
      },
      {
        id: 'added_at',
        header: t('date'),
        accessorKey: 'added_at',
        sort: true,
        cell: ({ cell }: { cell: any }) => <span>{formatDate(cell.getValue())}</span>,
      },
      {
        id: 'added_by_name',
        header: t('added_by'),
        accessorKey: 'added_by_name',
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
                <DropdownItem onClick={() => (onView(cell.getValue()), onClose())}>
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
                {/* <DeleteConfirmPop
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
                                /> */}
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
    loadData: (props: any) => fetchNotesTableData(props, entityId),
    paginate: true,
    rowSelection: false,
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableVers]);

  return <Table searchOption={false} isRowPerPageVisible={false} {...{ tableProperties }} />;
}

export default NotesList;
