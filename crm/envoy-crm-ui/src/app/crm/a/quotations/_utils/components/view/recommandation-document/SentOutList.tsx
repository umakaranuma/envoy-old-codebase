import { useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchGeneratedDocumentTableData } from '../../../service';
import { formatDate } from '@/helpers/services/commonService';
import FileDownloadButton from '@/components/others/page-related/uploader/FileDownloadButton';

function SentOutList({ quotationId }: { quotationId: string }) {
  const t = useTrans('label.quotations,otr.common');
  const tableName = 'sent_out';
  const [tableColumnVers, _setTableColumnVers] = useState(0);

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
        header: t('sent_date'),
        accessorKey: 'uploaded_date',
        sort: true,
        cell: ({ cell }: { cell: any }) => <span>{formatDate(cell.uploaded_date) || ''}</span>,
      },
      {
        id: 'uploaded_by_name',
        header: t('sent_by'),
        accessorKey: 'uploaded_by_name',
        sort: true,
      },
      {
        id: 'generated_pdf_name',
        header: t('document'),
        accessorKey: 'generated_pdf_name',
        cell: ({ cell }: { cell: any }) => <FileDownloadButton s3Key={cell.documents[0]?.coverage_details} fileType="pdf" />,
      },
    ],
    [],
  );

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: (props: any) => fetchGeneratedDocumentTableData(props, quotationId, 'sent'),
    paginate: true,
    rowSelection: false,
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers]);

  return <Table {...{ tableProperties, searchOption: false, isRowPerPageVisible: false, isPaginationTextVisible: false }} />;
}

export default SentOutList;
