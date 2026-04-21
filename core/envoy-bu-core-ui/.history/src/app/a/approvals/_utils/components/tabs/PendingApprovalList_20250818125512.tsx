import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { useRouter } from 'next/navigation';
import { Badge } from '@apptimus-ui/ui-element';
import { formatDate } from '@/helpers/services/commonService';
import { fetchApprovalTableData } from '../../service';
import ApprovalConfirmation from '../ApprovalConfirmation';

function PendingApprovalList({ tableVers, onView }: { tableVers: number; onView: Function }) {
  const t = useTrans('label.approvals,otr.common');
  const tableName = 'pending_approvals';
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const router = useRouter();
  const [selectedOperation, setSelectedOperation] = useState({ status: '', id: '' });

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
        header: t('request_type'),
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
        id: 'opportunity_type_title',
        header: t('opportunity'),
        accessorKey: 'opportunity_type_title',
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
                    <Flexicon icon="pencil-line" variant="line" size={17} />
                    <span>{t('edit')}</span>
                  </span>
                </DropdownItem>
                <DropdownItem onClick={() => (setIsFullscreen(false), setSelectedOperation({ status: 'approved', id: cell.getValue() }), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="check-circle" variant="line" size={17} />
                    <span>{t('approve')}</span>
                  </span>
                </DropdownItem>
                <DropdownItem onClick={() => (setIsFullscreen(false), setSelectedOperation({ status: 'rejected', id: cell.getValue() }), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="x-square" variant="line" size={17} />
                    <span>{t('reject')}</span>
                  </span>
                </DropdownItem>
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
    loadData: (props: any) => fetchApprovalTableData(props, 'pending'),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'approval_id',
      mode: 'single',
      enableSelectAll: true,
      action: (selectedId: string) => router.push(`/a/approvals/${selectedId}`),
    },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers, tableVers]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : ''}`}>
        <Table heading={<PageHeading title={t('approvals')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen }} />
      </div>
      <CustomizeColumn
        key={tableColumnVers}
        isOpen={isCustColumnVisible}
        tableName={tableName}
        columns={tableColumns}
        onClose={() => setIsCustColumnVisible(false)}
        afterUpdate={() => setTableColumnVers((prevTableColumnVers) => prevTableColumnVers + 1)}
      />
      {selectedOperation.id !== '' && (
        <ApprovalConfirmation
          isOpen={selectedOperation.id !== ''}
          onCancel={() => setSelectedOperation({ status: '', id: '' })}
          afterSave={() => {
            setSelectedOperation({ status: '', id: '' }), tableProperties.reload();
          }}
          currentId={selectedOperation.id}
          status={selectedOperation.status}
        />
      )}
    </>
  );
}

export default PendingApprovalList;
