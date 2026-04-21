import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import { formatDate } from '@/helpers/services/commonService';
import { fileReceiver } from '@/helpers/services/storageService';
import { fetchAllIssuedPolicyDocumentTableData } from '../../../../service';
import FileDownloadButton from '@/components/others/page-related/uploader/FileDownloadButton';

function RiskRelatedList({ onEdit, tableVers, handleOnDelete, policyId }: { onEdit: Function; tableVers: number; handleOnDelete: Function; policyId: string }) {
  const t = useTrans('label.policy_request,otr.common');
  const [tableColumnVers, _setTableColumnVers] = useState(0);

  const handleFileViewer = async (key: string) => {
    const file = await fileReceiver({ key });
    window.open(file);
  };

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'file_name',
        header: t('file_name'),
        accessorKey: 'file_name',
        sort: true,
        cell: ({ cell }: { cell: any }) => <FileDownloadButton s3Key={cell.doc} fileName={cell.file_name} fileType={cell.file_type || 'pdf'} />,
      },
      {
        id: 'file_type',
        header: t('document_type'),
        accessorKey: 'file_type',
        sort: true,
        align: 'center',
      },
      {
        id: 'created_by',
        header: t('uploaded_by'),
        accessorKey: 'created_by',
        sort: true,
      },
      {
        id: 'created_at',
        header: t('uploaded_on'),
        accessorKey: 'created_at',
        sort: true,
        cell: ({ cell }: { cell: any }) => <>{formatDate(cell.created_at)}</>,
      },
      {
        id: 'notes',
        header: t('notes'),
        accessorKey: 'notes',
        sort: true,
        cell: ({ cell }: { cell: any }) => <>{cell.notes || '-'}</>,
        align: 'center',
        styles: {
          body: {
            td: { textWrap: 'nowrap' },
          },
        },
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
                <DropdownItem onClick={() => (handleFileViewer(cell.doc), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="eye" variant="line" size={17} />
                    <span>{t('view')}</span>
                  </span>
                </DropdownItem>
                <DropdownItem onClick={() => (onEdit(cell.getValue()), onClose())}>
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
                />
              </span>
            )}
          </Dropdown>
        ),
        customizable: false,
      },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchAllIssuedPolicyDocumentTableData(props, policyId, 'risk-related'),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'doc',
      mode: 'single',
      action: (selectedId: string) => handleFileViewer(selectedId),
    },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers, tableVers]);

  return <Table {...{ tableProperties, searchOption: false, recordControl: false }} />;
}

export default RiskRelatedList;
