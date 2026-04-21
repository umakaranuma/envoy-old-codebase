import React, { useEffect, useMemo, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { useAsyncTable } from '@apptimus-ui/table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import Table from '@/components/table-properties/Table';
import PageHeading from '@/components/others/PageHeading';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import { fetchTeamTableData } from '../service';
import { formatDate } from '@/helpers/services/commonService';

interface Props {
  onEdit: (id: string) => void;
  onView: (id: string) => void;
  handleOnDelete: (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => void;
  tableVers: number;
}

const TeamList: React.FC<Props> = ({ onEdit, onView, handleOnDelete, tableVers }) => {
  const t = useTrans('label.teams,otr.common');
  const [isFullscreen, setIsFullscreen] = useState(false);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'name',
        header: t('team_name'),
        accessorKey: 'name',
        sort: true,
      },
      {
        id: 'name',
        header: t('native_product'),
        accessorKey: 'name',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'manager_name',
        header: t('team_lead'),
        accessorKey: 'manager_name',
        sort: true,
      },
      {
        id: 'created_at',
        header: t('created_on'),
        accessorKey: 'created_at',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div>{formatDate(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'updated_at',
        header: t('last_updated_on'),
        accessorKey: 'updated_at',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div>{formatDate(cell.getValue()) || '-'}</div>,
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
                  deleteId={cell.getValue()}
                  {...{ handleOnDelete, onClose }}
                />
              </span>
            )}
          </Dropdown>
        ),
      },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchTeamTableData(props),
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
  }, [tableVers]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-2'}`}>
        <Table heading={<PageHeading title={t('native_products')} icon="sun-light" />} tableProperties={tableProperties} isFullscreen={isFullscreen} setIsFullscreen={setIsFullscreen} />
      </div>
    </>
  );
};

export default TeamList;
