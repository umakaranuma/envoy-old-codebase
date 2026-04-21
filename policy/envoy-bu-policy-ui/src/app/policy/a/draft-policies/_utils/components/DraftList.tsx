import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { formatDate, hexToRgba } from '@/helpers/services/commonService';
import { useRouter } from 'next/navigation';
import FileDownloadButton from '@/components/others/page-related/uploader/FileDownloadButton';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import { fetchDraftPoliciesTableData } from '../service';

function DraftList() {
  const t = useTrans('label.policy_request,label.draft_policies,otr.common');
  const tableName = 'draft_policies';
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const router = useRouter();

  const onEdit = (id: number, type: string, customerId: string, customerType: string) => {
    router.push(`/policy/a/policy-request/create?draftId=${id}&ip=${type === 'policy' ? 'true' : 'false'}&cusId=${customerId}&ct=${customerType === 'Corporate' ? 1 : 0}`);
  };

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'insurer_name',
        header: t('insurer_company_name'),
        accessorKey: 'insurer_name',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'issued_policy_code',
        header: t('policy_request_id'),
        accessorKey: 'issued_policy_code',
        sort: true,
        cell: ({ cell }: { cell: any }) => <>{cell.issued_policy_code ? cell.issued_policy_code : cell.request_policy_code || '-'}</>,
      },
      {
        id: 'created_at',
        header: t('request_date'),
        accessorKey: 'created_at',
        sort: true,
        cell: ({ cell }: { cell: any }) => <>{formatDate(cell.created_at)}</>,
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
        id: 'request_type_name',
        header: t('request_type'),
        accessorKey: 'request_type_name',
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
            style={{ background: hexToRgba(cell.status_color || '', 0.1), border: `1px solid ${cell.status_color}`, color: cell.status_color }}
            onClick={onClick}
          >
            {cell.status_name}
          </div>
        ),
      },
      {
        id: 'created_by_name',
        header: t('requested_by'),
        accessorKey: 'created_by_name',
        sort: true,
      },
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
                <DropdownItem onClick={() => (setIsFullscreen(false), onEdit(cell.policy_base_id, cell.type, cell.customer_id, cell.customer_type), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="pencil-line" variant="line" size={17} />
                    <span>{t('edit')}</span>
                  </span>
                </DropdownItem>
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
    loadData: (props: any) => fetchDraftPoliciesTableData(props),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'policy_base_id',
      mode: 'single',
      enableSelectAll: true,
      action: (_selectedId: string, data: any) => {
        onEdit(data.policy_base_id, data.type, data.customer_id, data.customer_type);
      },
    },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
        <Table heading={<PageHeading title={t('draft_policies')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible }} />
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

export default DraftList;
