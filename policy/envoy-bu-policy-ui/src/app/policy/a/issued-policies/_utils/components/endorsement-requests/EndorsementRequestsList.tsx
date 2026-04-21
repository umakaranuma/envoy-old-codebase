import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchEndorsementRequestTableData } from '../../service';
import { useParams } from 'next/navigation';
import { formatDate } from '@/helpers/services/commonService';
import ChatContent from './ChatContent';

function EndorsementRequestsList({
  tableVers,
  setEmailData,
  setapproveFormVisible,
  setApproveId,
}: {
  tableVers: number;
  setEmailData: Function;
  setapproveFormVisible: Function;
  setApproveId: Function;
}) {
  const t = useTrans('label.issued_policies,otr.common');
  const [tableColumnVers, _setTableColumnVers] = useState(0);
  const params = useParams();
  const policyId = params.policyId?.toString() || '';

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'endorsement_request',
        header: t('request_id'),
        accessorKey: 'endorsement_request',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'created_at',
        header: t('requested_date'),
        accessorKey: 'created_at',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div>{formatDate(cell.created_at)}</div>,
      },
      {
        id: 'endorsement_type_name',
        header: t('endorsement_type'),
        accessorKey: 'endorsement_type_name',
        sort: true,
      },
      {
        id: 'created_by',
        header: t('requested_by'),
        accessorKey: 'created_by',
        sort: true,
      },
      {
        id: 'remarks',
        header: t('remarks'),
        accessorKey: 'remarks',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div>{cell.remarks || '-'}</div>,
      },
      {
        header: t('action'),
        align: 'center',
        accessorKey: 'id',
        cell: ({ cell }: { cell: any }) => (
          <>
            {cell.is_processed === 0 && cell.mail_status === 0 && (
              <Dropdown
                trigger={
                  <span className="action-icon">
                    <Flexicon icon="dots-horizontal" variant="line" size={17} />
                  </span>
                }
              >
                {(onClose: Function) => (
                  <span className="t-action">
                    {cell.is_processed === 0 && (
                      <DropdownItem
                        onClick={() => {
                          setapproveFormVisible(true);
                          setApproveId(cell.id, cell.endorsement_type_name);
                          onClose();
                        }}
                      >
                        <span className="d-flex gap-2">
                          <Flexicon icon="check-circle" variant="line" size={17} />
                          <span>{t('accept')}</span>
                        </span>
                      </DropdownItem>
                    )}
                    {cell.mail_status === 0 && (
                      <DropdownItem
                        onClick={() => (
                          setEmailData({ id: cell.id, insurer_name: cell.insurer_name, policy_holder_name: cell.policy_holder_name, policy_id: cell.policy_id, effective_date: cell.effective_date }),
                          onClose()
                        )}
                      >
                        <span className="d-flex gap-2">
                          <Flexicon icon="mail-01" variant="line" size={17} />
                          <span>{t('email')}</span>
                        </span>
                      </DropdownItem>
                    )}
                  </span>
                )}
              </Dropdown>
            )}
          </>
        ),
        customizable: false,
      },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchEndorsementRequestTableData(props, policyId),
    paginate: true,
    rowExpandable: {
      primaryKey: 'id',
      expandableRows: () => true,
      expandedRowRender: (record: any) => {
        return (
          <>
            <ChatContent policyId={policyId} endoresementId={record.id} />
          </>
        );
      },
    },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers, tableVers]);

  return <Table searchOption={false} isRowPerPageVisible={false} {...{ tableProperties }} />;
}

export default EndorsementRequestsList;
