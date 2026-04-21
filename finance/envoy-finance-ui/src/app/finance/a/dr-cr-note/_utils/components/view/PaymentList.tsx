import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { formatDate, thousandSeparator } from '@/helpers/services/commonService';
import { fetchPaymentTableData } from '../../service';
import PageHeading from '@/components/others/PageHeading';
import { getCurrency } from '@/helpers/services/currencyService';
import FilePreviewer from '@/components/others/page-related/FilePreviewer';

export default function PaymentList({ tableVersion: tableColumnVers, invoiceId }: { tableVersion: number; invoiceId: string }) {
  const t = useTrans('label.payments,label.invoice,otr.common');
  const currency = getCurrency();
  const [isFullscreen, setIsFullscreen] = useState(false);
  // const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  // const [tableVersion, setTableVersion] = useState(tableColumnVers);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'receipt_number',
        header: t('receipt_number'),
        accessorKey: 'receipt_number',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'payment_created_at',
        header: t('date'),
        accessorKey: 'payment_created_at',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <>{formatDate(cell.payment_created_at) || cell.getValue() || '-'}</>,
      },
      {
        id: 'total_amt',
        header: `${t('total_amount')} (${currency.code})`,
        accessorKey: 'total_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) ?? '_'}</div>,
      },
      {
        id: 'paid_amount',
        header: `${t('paid_amount')} (${currency.code})`,
        accessorKey: 'paid_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) ?? '_'}</div>,
      },
      {
        id: 'outstanding_amount',
        header: `${t('outstanding_amount')} (${currency.code})`,
        accessorKey: 'outstanding_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) ?? '_'}</div>,
      },
      {
        id: 'payment_receipt',
        header: t('payment_receipt'),
        accessorKey: 'payment_receipt',
        sort: true,
        cell: ({ cell }: { cell: any }) => <FilePreviewer fileName={t('payment_receipt')} s3Url={`${process.env.S3CDN}/${cell.doc}`} fileType={cell.doc_type} downloadFileName={cell.receipt_number} />,
      },
      {
        id: 'remarks',
        header: t('remarks'),
        accessorKey: 'remarks',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
    ],
    [t],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchPaymentTableData(props, invoiceId),
    paginate: true,
    rowSelection: false,
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
        <Table heading={<PageHeading title={t('payments')} icon="sun-light" />} searchOption={true} isRowPerPageVisible={false} {...{ tableProperties, isFullscreen, setIsFullscreen }} />
      </div>
      {/* <CustomizeColumn
        key={tableVersion}
        isOpen={isCustColumnVisible}
        tableName={tableName}
        columns={tableColumns}
        onClose={() => setIsCustColumnVisible(false)}
        afterUpdate={() => setTableVersion((prev) => prev + 1)}
      /> */}
    </>
  );
}
