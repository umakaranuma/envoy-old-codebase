import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchPolicyRequestTableData } from '../services';
import { hexToRgba } from '@/helpers/services/commonService';
import { useRouter } from 'next/navigation';
import FileDownloadButton from '@/components/others/page-related/uploader/FileDownloadButton';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';

function PolicyRequestList({
  onIssue,
  tableVersion,
  // handleDocExtraction,
  // setCurrentPolicyRequestId,
}: {
  onIssue: Function;
  tableVersion: number;
  // handleDocExtraction: Function;
  // setCurrentPolicyRequestId: Function;
}) {
  const t = useTrans('label.policy_request,otr.common');
  const tableName = 'polices_requests';
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const router = useRouter();

  const onView = (id: number) => {
    router.push(`/policy/a/policy-request/${id}`);
  };

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'insurer_company_name',
        header: t('insurer_company_name'),
        accessorKey: 'insurer_company_name',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'policy_request_id',
        header: t('policy_request_id'),
        accessorKey: 'policy_request_id',
        sort: true,
      },
      {
        id: 'policy_request_date',
        header: t('request_date'),
        accessorKey: 'policy_request_date',
        sort: true,
      },
      {
        id: 'quotation_document_name',
        header: t('quotation_document'),
        accessorKey: 'quotation_document_name',
        sort: true,
        align: 'center',
        cell: ({ cell }: { cell: any }) => <FileDownloadButton s3Key={cell.quotation_document} fileType="pdf" />,
      },
      {
        id: 'request_type',
        header: t('request_type'),
        accessorKey: 'request_type',
        sort: true,
      },
      {
        id: 'customer_name',
        header: t('customer_name'),
        accessorKey: 'customer_name',
        sort: true,
      },
      {
        id: 'status',
        header: t('status'),
        accessorKey: 'status',
        sort: true,
        cell: ({ cell, onClick }: any) => (
          <div
            className="rounded-5 fw-semibold badge"
            style={{ background: hexToRgba(cell?.status?.color || '', 0.1), border: `1px solid ${cell?.status?.color}`, color: cell?.status?.color }}
            onClick={onClick}
          >
            {cell?.status?.name}
          </div>
        ),
      },
      // {
      //   id: 'created_by',
      //   header: t('requested_by'),
      //   accessorKey: 'created_by',
      //   sort: true,
      // },
      // {
      //   id: 'insurer_notes',
      //   header: t('remarks'),
      //   accessorKey: 'insurer_notes',
      //   sort: true,
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
              <span className="t-action">
                <DropdownItem onClick={() => (setIsFullscreen(false), onView(cell.getValue()), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="eye" variant="line" size={17} />
                    <span>{t('view')}</span>
                  </span>
                </DropdownItem>
                {(cell.status?.type === 'pol_pending_iss' || cell.status?.type === 'pol_renewal_progress') && (
                  <DropdownItem onClick={() => (setIsFullscreen(false), onIssue(cell.getValue()), onClose())}>
                    <span className="d-flex gap-2">
                      <Flexicon icon="heart-hand" variant="line" size={17} />
                      <span>{t('create_policy')}</span>
                    </span>
                  </DropdownItem>
                )}
                {/* <DropdownItem onClick={() => (setIsFullscreen(false), onEdit(cell.getValue()), onClose())}>
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
    loadData: (props: any) => fetchPolicyRequestTableData(props),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
      enableSelectAll: true,
      action: (selectedId: string) => {
        router.push(`/policy/a/policy-request/${selectedId}`);
      },
    },
    // rowExpandable: {
    //   primaryKey: 'id',
    //   expandableRows: () => true,
    //   expandedRowRender: (record: any) => {
    //     return (
    //       <>
    //         <ChatContent
    //           id={record.id}
    //           handleDocExtraction={(data: IFilePreviewer) => {
    //             handleDocExtraction(data);
    //           }}
    //           setCurrentPolicyRequestId={setCurrentPolicyRequestId}
    //         />
    //       </>
    //     );
    //   },
    // },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers, tableVersion]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
        <Table heading={<PageHeading title={t('create_policy')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible }} />
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

export default PolicyRequestList;
