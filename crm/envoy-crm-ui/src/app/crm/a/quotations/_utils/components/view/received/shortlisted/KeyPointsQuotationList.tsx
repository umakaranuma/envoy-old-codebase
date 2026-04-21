import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchAllGenerateDocumentListedTableData } from '../../../../service';
import { thousandSeparator } from '@/helpers/services/commonService';

function KeyPointsQuotationList({ selectedColumns, selectedQuotations, quotationId }: { selectedColumns: { title: string; column: string }[]; selectedQuotations: string[]; quotationId: string }) {
  const t = useTrans('label.quotations,otr.common');

  const allColumns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'code',
        header: t('code'),
        accessorKey: 'code',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: any) => <>{cell.getValue()}</>,
      },
      {
        id: 'service_provider_name',
        header: t('insurer_company_name'),
        accessorKey: 'service_provider_name',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
      },
      {
        id: 'version',
        header: t('quotation_version'),
        accessorKey: 'version',
        sort: true,
        cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
        align: 'center',
      },
      {
        id: 'QuotationRequestNumber',
        header: t('quotation_request_number'),
        accessorKey: 'QuotationRequestNumber',
        sort: true,
        cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
        align: 'center',
      },
      {
        id: 'total_amount',
        header: t('quotation_value'),
        accessorKey: 'total_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'received_date',
        header: t('received_date'),
        accessorKey: 'received_date',
        sort: true,
        cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
        align: 'center',
      },
      {
        id: 'expiry_date',
        header: t('expiry_date'),
        accessorKey: 'expiry_date',
        sort: true,
        cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
        align: 'center',
      },
      {
        id: 're_request',
        header: t('re_request'),
        accessorKey: 're_request',
        sort: true,
        cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
        align: 'center',
      },
      {
        id: 'review',
        header: t('review'),
        accessorKey: 'review',
        sort: true,
        cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
        align: 'center',
      },
    ],
    [],
  );

  const columns = useMemo(() => allColumns.filter((column) => column.id && selectedColumns.some((selected) => selected.column === column.id)), [allColumns, selectedColumns]);

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: () => fetchAllGenerateDocumentListedTableData(quotationId, selectedQuotations),
    paginate: true,
    rowSelection: false,
  });

  useEffect(() => {
    tableProperties.reload();
  }, [selectedQuotations.length]);

  return (
    <>
      <div className={`data-table-container pb-4`}>
        <Table heading={<PageHeading title={t('quotation_management')} icon="sun-light" />} {...{ tableProperties, searchOption: false, recordControl: false }} />
      </div>
    </>
  );
}

export default KeyPointsQuotationList;
