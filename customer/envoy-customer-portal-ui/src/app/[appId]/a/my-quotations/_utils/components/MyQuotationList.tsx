import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchAllQuotationsTableData } from '../service';
import QuotationServiceProviderList from './QuotationServiceProviderList';
import { formatDate, hexToRgba } from '@/helpers/services/commonService';
import FileDownloadButton from '@/components/others/page-related/uploader/FileDownloadButton';

function MyQuotationList() {
  const t = useTrans('label.my_quotation,otr.common');
  const [tableVersion, setTableVersion] = useState(0);
  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'opportunity_type_names',
        header: t('product_type'),
        accessorKey: 'opportunity_type_names',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'code',
        header: t('quotation_id'),
        accessorKey: 'code',
        sort: true,
      },
      {
        id: 'requested_data',
        header: t('received_date'),
        accessorKey: 'requested_data',
        sort: true,
        cell: ({ cell }: { cell: any }) => {
          return <>{formatDate(cell.getValue())}</>;
        },
      },
      {
        id: 'expiry_date',
        header: t('expiration_date'),
        accessorKey: 'expiry_date',
        sort: true,
        cell: ({ cell }: { cell: any }) => {
          return <>{formatDate(cell.getValue())}</>;
        },
      },
      {
        id: 'status',
        header: t('status'),
        accessorKey: 'status',
        sort: true,
        cell: ({ cell, onClick }: any) => {
          return (
            <div
              className={`rounded-5 fw-semibold badge`}
              style={{
                background: hexToRgba(cell.status_color ? cell.status_color : '', 0.1),
                border: `1px solid ${hexToRgba(cell.status_color ? cell.status_color : '', 0.4)}`,
                color: cell.status_color ? cell.status_color : '',
              }}
              onClick={onClick}
            >
              {cell.status}
            </div>
          );
        },
        visibilityLock: false,
      },
      {
        id: 'coverage_details_name',
        header: t('document'),
        accessorKey: 'coverage_details_name',
        sort: true,
        cell: ({ cell }: { cell: any }) => <FileDownloadButton s3Key={cell.coverage_details} fileType="pdf" />,
        align: 'center',
      },
    ],
    [],
  );

  useEffect(() => {
    tableProperties.reload();
  }, [tableVersion]);

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchAllQuotationsTableData(props),
    paginate: true,
    rowSelection: false,
    rowExpandable: {
      primaryKey: 'id',
      expandableRows: () => true,
      expandedRowRender: (record) => {
        return <QuotationServiceProviderList quotationId={record.id} setTableVersion={setTableVersion} />;
      },
    },
  });

  return <Table {...{ tableProperties, searchOption: false }} />;
}

export default MyQuotationList;
