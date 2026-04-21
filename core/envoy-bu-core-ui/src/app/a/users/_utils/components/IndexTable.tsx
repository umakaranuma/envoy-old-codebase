import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useReducer, useState } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchUserTableData } from '../service';
import UserFilter from './UserFilter';
import { dataReducer, filterReducer } from '@/helpers/services/dataReducer';
import { convertToString } from '@/helpers/services/commonService';
import { getAllSalesTarget } from '../api-service';
import { Skeleton } from '@apptimus-ui/ui-element';

function IndexTable({
  tableVers,
  onView,
  onEdit,
  setSelectedUserId,
  setAddMembersInTeamVisible,
}: {
  tableVers: number;
  onView: Function;
  onEdit: Function;
  setSelectedUserId: any;
  setAddMembersInTeamVisible: any;
}) {
  const t = useTrans('label.user,otr.common');
  const tableName = 'users';
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const [filterComKey, setFilterComKey] = useState(0);
  const [isFilterVisible, setIsFilterVisible] = useState(false);
  const [salesTargetData, sDispatch] = useReducer(dataReducer, { loadingState: true, columnKeyVers: 0, data: {} });
  console.log(setSelectedUserId, setAddMembersInTeamVisible);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      // {
      //   id: 'salutation',
      //   header: t('salutation'),
      //   accessorKey: 'title',
      //   sort: true,
      // },
      // {
      //   id: 'first_name',
      //   header: t('first_name'),
      //   accessorKey: 'first_name',
      //   sort: true,
      //   visibilityLock: false,
      // },
      // {
      //   id: 'last_name',
      //   header: t('last_name'),
      //   accessorKey: 'last_name',
      //   sort: true,
      //   visibilityLock: false,
      // },
      {
        id: 'display_name',
        header: t('display_name'),
        accessorKey: 'display_name',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'code',
        header: t('staff_code'),
        accessorKey: 'code',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'role_name',
        header: t('user_role'),
        accessorKey: 'role_name',
        sort: true,
      },
      // {
      //   id: 'team_name',
      //   header: t('sales_team'),
      //   accessorKey: 'team_name',
      //   sort: true,
      //   cell: ({ cell }: { cell: any }) => {
      //     const teamName = cell.getValue();
      //     if (!teamName) {
      //       return (
      //         <div
      //           className="text-primary hover:underline pointer fw-semibold"
      //           onClick={() => {
      //             setAddMembersInTeamVisible(true);
      //             setSelectedUserId(cell.id);
      //           }}
      //         >
      //           Add Team
      //         </div>
      //       );
      //     }

      //     return <span>{teamName}</span>;
      //   },
      // },
      {
        id: 'email',
        header: t('email'),
        accessorKey: 'email',
        sort: true,
      },
      {
        id: 'contact_no',
        header: t('contact_number'),
        accessorKey: 'contact_no',
        sort: true,
      },
      // {
      //   id: 'team_line_manager',
      //   header: t('line_manager'),
      //   accessorKey: 'team_line_manager',
      //   sort: true,
      // },
      {
        id: 'status_name',
        header: t('status'),
        accessorKey: 'status_name',
        sort: true,
      },
      // {
      //   id: 'target_amount',
      //   header: t('sales_target'),
      //   accessorKey: 'target_amount',
      //   sort: true,
      //   cell: ({ cell }: { cell: any }) => (
      //     <div
      //       className="text pointer"
      //       onClick={() => {
      //         setSelectedUserId(cell.id);
      //       }}
      //     >
      //       <SaletargetCell key={`target-cell-${cell.id}`} {...{ salesTargetData, cell }} />
      //     </div>
      //   ),
      // },
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
              <>
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
                {/* <PopConfirm
                  trigger={<DropdownItem onClick={() => (setIsFullscreen(false))}>
                    <span className="d-flex gap-2">
                      <Flexicon icon="trash-03" variant="line" size={17} />
                      <span>{t('delete')}</span>
                    </span>
                  </DropdownItem>}
                  onConfirm={(callback) => {
                    //onResend();
                    alert('hii')
                    callback();
                  }}
                  onCancel={(callback) => {
                    callback();
                  }}
                /> */}
              </>
            )}
          </Dropdown>
        ),
        customizable: false,
      },
    ],
    [salesTargetData.columnKeyVers],
  );

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: (props: any) => fetchUserTableData(props),
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
      reducer: (_: any, action: any) => filterReducer({ action, setFilterComKey }),
    },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers, tableVers]);

  useEffect(() => {
    const fetchSalesTargetData = async () => {
      const IdString = convertToString(tableProperties.tableData, 'id');
      if (IdString) {
        sDispatch({ type: 'set-loader' });
        try {
          const responseData = await getAllSalesTarget({ ids: IdString });

          if (responseData.is_success) {
            sDispatch({ type: 'set-data', data: responseData.result });
          }
        } catch (error) {
          console.log(error);
        }
      }
    };

    fetchSalesTargetData();
  }, [tableProperties.tableData]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
        <Table heading={<PageHeading title={t('user_staff')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible, setIsFilterVisible }} />
      </div>
      <CustomizeColumn
        key={tableColumnVers}
        isOpen={isCustColumnVisible}
        tableName={tableName}
        columns={tableColumns}
        onClose={() => setIsCustColumnVisible(false)}
        afterUpdate={() => setTableColumnVers((prevTableColumnVers) => prevTableColumnVers + 1)}
      />
      <UserFilter
        key={`filter-${filterComKey}`}
        isOpen={isFilterVisible}
        onClose={() => setIsFilterVisible(false)}
        onSubmit={(filterData: any, isReset: boolean) => (setIsFilterVisible(false), tableProperties.tableDispatch({ filterData, isReset }))}
      />
    </>
  );
}

export default IndexTable;

export const SaletargetCell = ({ salesTargetData, cell }: { salesTargetData: any; cell: any }) => {
  // const t = useTrans('label.user,otr.common');

  if (salesTargetData.loadingState && cell.id) {
    return <Skeleton height="20px" key={`skeleton-${cell.id}`} />;
  }

  const targetData = salesTargetData.data.data.find((item: any) => item.user_id === parseInt(cell.id));

  if (targetData?.month_target_amount) {
    return (
      <div key={`target-${cell.id}`} className="text">
        {targetData?.month_target_amount}
      </div>
    );
  }

  // return (
  //   <div key={`set-target-${cell.id}`}>
  //      <Badge text= {t('set_sales_target')} color="danger" variant='light' />
  //   </div>
  // );
};
