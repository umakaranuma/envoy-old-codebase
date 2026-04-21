import React, { useEffect, useMemo, useState } from 'react';
import KanbanCard from './KanbanCard';
import { useAsyncTable } from '@apptimus-ui/table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useTrans } from '@/helpers/services/lang/langService';
import S3Avatar from '@/components/others/page-related/S3Avatar';
import { fetchAllAssignees } from '../../../service';
import { hasPermission } from '@/components/others/Permission';
import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';
import { Skeleton } from '@apptimus-ui/ui-element';
import RecordController from '@/components/table-properties/RecordController';

function KanbanView() {
  const t = useTrans('label.tasks');
  const [selectedAssignee, setSelectedAssignee] = useState('');
  const userTaskViewAllPerm = hasPermission('TASK', ['VIEW_ALL']);

  console.log('selectedAssignee', selectedAssignee);

  useEffect(() => {
    // if (!userTaskViewAllPerm) {
    //   const authUser = getLocalStorage(local_storage.auth_user_info);
    //   console.log('authUser', authUser);

    //   if (authUser) {
    //     setSelectedAssignee(authUser.id);
    //   }
    // }
    const authUser = getLocalStorage(local_storage.auth_user_info);
    if (authUser) {
      setSelectedAssignee(authUser.id);
    }
  }, []);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'name',
        header: t('users'),
        accessorKey: 'name',
        cell: ({ cell, onClick }: { cell: any; onClick: Function }) => {
          return (
            <div role="button" className="d-flex flex-row align-items-center gap-2" onClick={() => onClick()}>
              <div>
                <S3Avatar imageKey={undefined} width={35} height={35} />
              </div>
              <div className="fs-14 fw-medium">{cell.display_name}</div>
            </div>
          );
        },
        size: '15rem',
      },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: fetchAllAssignees,
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
      action: (id: string) => setSelectedAssignee(id),
    },
  });
  return (
    <>
      {tableProperties.isTbodyLoading ? (
        <Skeleton width={'100%'} height={'30'} />
      ) : (
        <div className="d-flex gap-2 mt-2">
          {userTaskViewAllPerm && (
            <div className="bg-white rounded-3 p-2">
              <div className="fw-bold p-2 fs-15">{t('users')}</div>
              <>
                {tableProperties.tableData.length > 0 ? (
                  <div className="px-2 d-flex flex-column justify-content-between h-100">
                    <div>
                      {tableProperties.tableData.map((data: any) => (
                        <div
                          className={`d-flex flex-row align-items-center gap-2 pointer my-2 p-2 border ${data.id.toString() === selectedAssignee.toString() ? 'border-primary' : ''} rounded-2 bg-light`}
                          key={data.id}
                          onClick={() => setSelectedAssignee(data.id.toString())}
                        >
                          <div>
                            <S3Avatar imageKey={data.picture} width={35} height={35} />
                          </div>
                          <div className="d-flex flex-column">
                            <div className="fs-13 fw-medium">{data.display_name}</div>
                            <div className="fs-12">{data.email}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="mb-4">{<RecordController tableProperties={tableProperties} isRowPerPageVisible={false} isPaginationTextVisible={true} isPaginationButtonVisible={true} />}</div>
                  </div>
                ) : (
                  <div className="p-3 text-center">{t('no_data_found')}</div>
                )}
              </>
            </div>
          )}
          <div className="w-100">
            <KanbanCard key={selectedAssignee} {...{ selectedAssignee }} />
          </div>
        </div>
      )}
    </>
  );
}

export default KanbanView;
