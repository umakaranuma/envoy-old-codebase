import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import PercentageBar from '@/components/others/page-related/PercentageBar';
import { fetchGeneratedDocumentTableData } from '../../../service';
import { formatDate } from '@/helpers/services/commonService';
import FileDownloadButton from '@/components/others/page-related/uploader/FileDownloadButton';

function DraftDocumentList({ onEdit, tableVers, onSend, onView, quotationId }: { onEdit: Function; tableVers: number; onSend: Function; onView: Function; quotationId: string }) {
  const t = useTrans('label.quotations,otr.common');

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'send_quotation_id',
        header: t('recommendation_doc_id'),
        accessorKey: 'send_quotation_id',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'version',
        header: t('version'),
        accessorKey: 'version',
        sort: true,
      },
      {
        id: 'uploaded_date',
        header: t('uploaded_date'),
        accessorKey: 'uploaded_date',
        sort: true,
        cell: ({ cell }: { cell: any }) => <>{formatDate(cell.getValue())}</>,
      },
      {
        id: 'uploaded_by_name',
        header: t('created_by'),
        accessorKey: 'uploaded_by_name',
        sort: true,
      },
      {
        id: 'customer_name',
        header: t('customer_name'),
        accessorKey: 'customer_name',
        sort: true,
        cell: ({ cell }: { cell: any }) => (cell.customer ? cell.customer.name : '-'),
      },
      {
        id: 'coverage_details_name',
        header: t('recommendation_document'),
        accessorKey: 'coverage_details_name',
        cell: ({ cell }: { cell: any }) =>
          cell.vendor_quotation_ids.length === 0 ? cell.documents.length > 0 && <FileDownloadButton s3Key={cell.documents[0].coverage_details} /> : <PercentageBar percentage={30} />,
      },
      {
        header: t('action'),
        align: 'center',
        accessorKey: 'send_quotation_id',
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
                {cell.vendor_quotation_ids.length === 0 && (
                  <DropdownItem onClick={() => (onView(cell.documents[0].coverage_details), onClose())}>
                    <span className="d-flex gap-2">
                      <Flexicon icon="eye" variant="line" size={17} />
                      <span>{t('view')}</span>
                    </span>
                  </DropdownItem>
                )}
                {cell.vendor_quotation_ids.length > 0 && (
                  <DropdownItem onClick={() => (onEdit(cell.getValue()), onClose())}>
                    <span className="d-flex gap-2">
                      <Flexicon icon="pencil-line" variant="line" size={17} />
                      <span>{t('edit')}</span>
                    </span>
                  </DropdownItem>
                )}
                {cell.vendor_quotation_ids.length === 0 && (
                  <DropdownItem
                    onClick={() => (
                      onSend({
                        id: cell.customer.id,
                        name: cell.customer.name,
                        send_quotation_id: cell.getValue(),
                        documents: cell.documents ? cell.documents.map((file: any) => ({ name: file.coverage_details_name, doc: file.coverage_details })) : [],
                      }),
                      onClose()
                    )}
                  >
                    <span className="d-flex gap-2">
                      <Flexicon icon="send-01" variant="line" size={17} />
                      <span>{t('send')}</span>
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

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchGeneratedDocumentTableData(props, quotationId, 'draft'),
    paginate: true,
    rowSelection: false,
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableVers]);

  return <Table {...{ tableProperties, searchOption: false, isRowPerPageVisible: false, isPaginationTextVisible: false }} />;
}

export default DraftDocumentList;
