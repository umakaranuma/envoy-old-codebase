import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import PageHeading from '@/components/others/PageHeading';
import { fetchPaymentTableData } from '../services';
import { formatDate, thousandSeparator } from '@/helpers/services/commonService';
import { getCurrency } from '@/helpers/services/currencyService';

export default function TableInView({ tableVersion: tableColumnVers, invoiceId }: { tableVersion: number; invoiceId: string }) {
  const t = useTrans('label.service_rendered,otr.common,be.msg');
  const currency = getCurrency();
  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'created_at',
        header: t('date'),
        accessorKey: 'created_at',
        sort: true,
        cell: ({ cell }: { cell: any }) => <>{formatDate(cell.created_at) || cell.getValue() || '-'}</>,
      },
      {
        id: 'outstanding_amount',
        header: `${t('outstanding_amount')} (${currency.code})`,
        accessorKey: 'outstanding_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'paid_amount',
        header: `${t('paid_amount')} (${currency.code})`,
        accessorKey: 'paid_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      // {
      //   id: 'payment_receipt',
      //   header: t('payment_receipt'),
      //   accessorKey: 'payment_receipt',
      //   sort: true,
      //   cell: ({ cell }: { cell: any }) => <FilePreviewer fileName={cell.receipt_name} s3Url={`${process.env.S3CDN}/${cell.receipt_url}`} fileType={cell.receipt_type} />,
      // },
      {
        id: 'display_name',
        header: t('added_by'),
        accessorKey: 'display_name',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
    ],
    [],
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
      <div>
        <Table heading={<PageHeading title={t('payments')} icon="sun-light" />} isRowPerPageVisible={false} {...{ tableProperties, searchOption: false }} />
      </div>
    </>
  );
}
