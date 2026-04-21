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
import { useRouter } from 'next/navigation';

function RejectedList({ onView }: { onView: Function }) {
  const t = useTrans('label.approvals,otr.common');
  const tableName = 'pending_approvals';
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [tableColumnVers, _setTableColumnVers] = useState(0);
  const router = useRouter();

  const onReRequest = (policyBaseId: string, customerId: string) => {
    router.push(`/policy/a/policy-request/create?draftId=${policyBaseId}&rr=true&cusId=${customerId}`);
  };

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
                {cell.entity_type === 'policy' && (
                  <DropdownItem onClick={() => (setIsFullscreen(false), onReRequest(cell.policy_base_id, cell.customer_id), onClose())}>
                    <span className="d-flex gap-2">
                      <Flexicon icon="reverse-right" variant="line" size={17} />
                      <span>{t('re_request')}</span>
                    </span>
                  </DropdownItem>
                )}
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
    loadData: (props: any) => fetchApprovalTableData(props, 'rejected'),
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

export default RejectedList;
