import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import { fetchProductTeamTableData } from '../../../services';
import { formatDate } from '@/helpers/services/commonService';

function TeamsList({ viewId, tableVers, handleOnDelete, isEdit = false }: { viewId: string; tableVers: number; handleOnDelete: any; isEdit: boolean }) {
  const t = useTrans('label.products,otr.common');
  const [isFullscreen, setIsFullscreen] = useState(false);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'name',
        header: t('name'),
        accessorKey: 'name',
        sort: true,
      },
      {
        id: 'manager_name',
        header: t('team_lead'),
        accessorKey: 'manager_name',
        sort: true,
        cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
      },
      {
        id: 'latest_created_at',
        header: t('assigned_since'),
        accessorKey: 'latest_created_at',
        sort: true,
        cell: ({ cell }: any) => <div>{formatDate(cell.getValue()) || '-'}</div>,
      },
      ...(isEdit
        ? [
            {
              id: 'actions',
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
          ]
        : []),
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (params: any) => fetchProductTeamTableData(params, viewId),
    paginate: true,
  });

  useEffect(() => {
    tableProperties.reload();
  }, [viewId, tableVers]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-3'}`}>
        <Table heading={<PageHeading title={t('team_details')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, searchOption: false, enableTopContent: false }} />
      </div>
    </>
  );
}

export default TeamsList;
