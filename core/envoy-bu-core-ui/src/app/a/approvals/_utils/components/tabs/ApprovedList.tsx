import { useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchApprovalTableData } from '../../service';
import { Badge } from '@apptimus-ui/ui-element';
import { formatDate } from '@/helpers/services/commonService';

function ApprovedList({ onView }: { onView: Function }) {
  const t = useTrans('label.approvals,otr.common');
  const tableName = 'pending_approvals';
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [tableColumnVers, _setTableColumnVers] = useState(0);
  // const router = useRouter();

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'code',
        header: t('request_id'),
        accessorKey: 'code',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'entity_type',
        header: t('category'),
        accessorKey: 'entity_type',
        sort: true,
        visibilityLock: false,
        align: 'center',
        cell: ({ cell }: { cell: any }) => <Badge text={cell.getValue()} color={cell.getValue() === 'policy' ? 'primary' : 'warning'} radius="pill" />,
      },
      {
        id: 'request_type',
        header: t('transaction_type'),
        accessorKey: 'request_type',
        sort: true,
      },
      {
        id: 'request_date',
        header: t('requested_on'),
        accessorKey: 'request_date',
        sort: true,
        align: 'center',
        cell: ({ cell }: { cell: any }) => <div>{formatDate(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'opportunity_title',
        header: t('lead'),
        accessorKey: 'opportunity_title',
        sort: true,
      },
      {
        id: 'display_name',
        header: t('customer'),
        accessorKey: 'display_name',
        sort: true,
      },
      // {
      //   id: 'approval_status',
      //   header: t('approval_status'),
      //   accessorKey: 'approval_status',
      //   sort: true,
      //   visibilityLock: false,
      //   cell: ({ cell, onClick }: any) => {
      //     return (
      //       <div className="d-flex justify-content-between align-items-center gap-3" onClick={onClick}>
      //         <div
      //           className={`d-flex flex-row align-items-center gap-1 rounded-1 fs-10 fw-bold badge`}
      //           style={{ background: hexToRgba('#28a745', 0.1), border: `1px solid #28a745`, color: '#28a745' }}
      //         >
      //           <svg width="9" height="8" viewBox="0 0 9 8" fill="none" xmlns="http://www.w3.org/2000/svg">
      //             <circle cx="4.375" cy="4" r="3" fill={'#28a745'} />
      //           </svg>
      //           {cell.approval_status}
      //         </div>
      //       </div>
      //     );
      //   },
      // },
      // {
      //   id: 'remarks',
      //   header: t('notes'),
      //   accessorKey: 'remarks',
      //   sort: true,
      //   visibilityLock: false,
      //   cell: ({ cell }: { cell: any }) => (<div>{cell.getValue() || '-'}</div>),
      // },
      {
        header: t('action'),
        align: 'center',
        accessorKey: 'approval_id',
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
                {/* <DropdownItem onClick={() => (setIsFullscreen(false), setCurrentApprovalId(cell.getValue()), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="check-circle" variant="line" size={17} />
                    <span>{t('approve')}</span>
                  </span>
                </DropdownItem> */}
                {/* <DeleteConfirmPop
                  trigger={
                    <DropdownItem onClick={() => null}>
                      <span className="d-flex gap-2 w-100">
                        <Flexicon icon="trash-03" variant="line" size={17} />
                        <span>{t('delete')}</span>
                      </span>
                    </DropdownItem>
                  }
                  deleteId={cell.approval_id}
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

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: (props: any) => fetchApprovalTableData(props, 'approved'),
    paginate: true,
    rowSelection: false,
    // rowSelectionProp: {
    //   key: 'approval_id',
    //   mode: 'single',
    //   enableSelectAll: true,
    //   action: (selectedId: string) => router.push(`/a/approvals/${selectedId}`),
    // },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : ''}`}>
        <Table heading={<PageHeading title={t('partners')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen }} />
      </div>
      {/* <CustomizeColumn
        key={tableColumnVers}
        isOpen={isCustColumnVisible}
        tableName={tableName}
        columns={tableColumns}
        onClose={() => setIsCustColumnVisible(false)}
        afterUpdate={() => setTableColumnVers((prevTableColumnVers) => prevTableColumnVers + 1)}
      /> */}
    </>
  );
}

export default ApprovedList;
