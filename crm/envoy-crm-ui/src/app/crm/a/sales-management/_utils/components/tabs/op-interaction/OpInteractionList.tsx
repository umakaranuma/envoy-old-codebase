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
import { useParams } from 'next/navigation';
import { fetchAllOpInteractionTableData } from '../../../services';
import { Button } from '@apptimus-ui/ui-element';

function OpInteractionList({
  tableVers,
  onView,
  onEdit,
  handleOnDelete,
  setCreateFormVisible,
}: {
  tableVers: number;
  onView: Function;
  onEdit: Function;
  handleOnDelete: Function;
  setCreateFormVisible: Function;
}) {
  const t = useTrans('label.tasks,otr.common');
  const tableName = 'tasks';
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const params = useParams();
  const opportunityId = params.managementId?.toString() || '';
  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'date',
        header: t('date'),
        accessorKey: 'date',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'channel_name',
        header: t('channel'),
        accessorKey: 'channel_name',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'contact_by_display_name',
        header: t('contact_by'),
        accessorKey: 'contact_by_display_name',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'notes',
        header: t('remarks'),
        accessorKey: 'notes',
        sort: true,
        visibilityLock: false,
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
    loadData: (props: any) => fetchAllOpInteractionTableData(props, opportunityId),
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
      <div className={`data-table-container card custom-card px-2`}>
        <div className="d-flex justify-content-between align-items-center mb-3 mt-2">
          <div className="datatable-search">{tableProperties.SearchInput as React.ReactNode}</div>
          <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('add_new')}</span>
          </Button>
        </div>
        <Table heading={<PageHeading title={t('interaction')} />} searchOption={false} {...{ tableProperties }} />
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

export default OpInteractionList;
