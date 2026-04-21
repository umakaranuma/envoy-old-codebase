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
import { fetchNotesOpportunityTableData } from '../../../services';
import { Button } from '@apptimus-ui/ui-element';
import S3Avatar from '@/components/others/page-related/S3Avatar';

function NoteList({
  tableVers,
  handleOnDelete,
  onEdit,
  setCreateFormVisible,
  entityId,
}: {
  tableVers: number;
  onDelete: Function;
  handleOnDelete: Function;
  onEdit: Function;
  setCreateFormVisible: Function;
  entityId: string;
}) {
  const t = useTrans('label.sales_managements,otr.common');
  const tableName = 'notes';
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'notes',
        header: t('notes'),
        accessorKey: 'notes',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => {
          if (cell.is_high_priority === 1) {
            return (
              <>
                {cell.notes}
                <div className="text-primary">{t('high_priority')}</div>
              </>
            );
          }
          return <>{cell.notes}</>;
        },
      },
      {
        id: 'added_at',
        header: t('date'),
        accessorKey: 'added_at',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => {
          const isoDate = cell.added_at;
          const date = new Date(isoDate);
          return <>{date.toISOString().split('T')[0]}</>;
        },
      },
      {
        id: 'added_by_name',
        header: t('added_by'),
        accessorKey: 'added_by_name',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => {
          return (
            <>
              <S3Avatar imageKey={undefined} />
              {cell.added_by_name}
            </>
          );
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

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: (props: any) => fetchNotesOpportunityTableData(props, entityId),
    paginate: true,
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers, tableVers]);

  return (
    <>
      <div className={`data-table-container card custom-card px-4`}>
        <div className="d-flex justify-content-between align-items-center mb-3 mt-2">
          <div className="datatable-search">{tableProperties.SearchInput as React.ReactNode}</div>
          <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('add_new')}</span>
          </Button>
        </div>

        <Table heading={<PageHeading title={t('notes')} icon="sun-light" />} searchOption={false} {...{ tableProperties }} />
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

export default NoteList;
