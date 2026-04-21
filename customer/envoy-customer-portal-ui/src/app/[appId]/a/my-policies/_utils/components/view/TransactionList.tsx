import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchAllPolicyTransactionTableData } from '../../service';
import FileDownloadButton from '@/components/others/page-related/uploader/FileDownloadButton';
import { thousandSeparator } from '@/helpers/services/commonService';

function TransactionList({ policyId, tableVers }: { policyId: string; tableVers: string }) {
  const t = useTrans('label.my_policy,otr.common');

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      // {
      //   id: 'reference_id',
      //   header: t('transaction_id'),
      //   accessorKey: 'reference_id',
      //   visibilityLock: false,
      // },
      {
        id: 'invoice_type',
        header: t('transaction_type'),
        accessorKey: 'invoice_type',
      },
      {
        id: 'invoice_number',
        header: t('debit_note_number'),
        accessorKey: 'invoice_number',
      },
      {
        id: 'total_amount',
        header: t('total_amount'),
        accessorKey: 'total_amount',
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => <span>{thousandSeparator(cell.getValue())}</span>,
      },
      {
        id: 'paid_amount',
        header: t('payment_amount'),
        accessorKey: 'paid_amount',
        cell: ({ cell }: { cell: any }) => <span style={{ color: '#09729A' }}>{thousandSeparator(cell.getValue())}</span>,
      },
      // {
      //   id: 'confirm_receipt',
      //   header: t('debit_note'),
      //   accessorKey: 'confirm_receipt',
      //   cell: ({ cell }: { cell: any }) => <> {cell.confirm_receipt ? <FileDownloadButton s3Key={cell.confirm_receipt} fileType="pdf" /> : 'N/A'}</>,
      //   align: 'center',
      // },
      {
        id: 'confirm_receipt',
        header: t('confirmation_receipt'),
        accessorKey: 'confirm_receipt',
        cell: ({ cell }: { cell: any }) => <> {cell.confirmation_doc?.url ? <FileDownloadButton s3Key={cell.confirmation_doc?.url} fileType="pdf" /> : 'N/A'}</>,
        align: 'center',
      },
      {
        id: 'receipt',
        header: t('payment_receipt'),
        accessorKey: 'receipt',
        cell: ({ cell }: { cell: any }) => <> {cell.receipt ? <FileDownloadButton s3Key={cell.receipt} fileType="pdf" /> : 'N/A'}</>,
        align: 'center',
      },
    ],
    [],
  );

  useEffect(() => {
    tableProperties.reload();
  }, [tableVers]);

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchAllPolicyTransactionTableData(props, policyId),
    paginate: true,
    rowSelection: false,
  });

  return (
    <>
      <div className={`px-1 m-3 border border border-primary rounded-2`}>
        <Table {...{ tableProperties, searchOption: false, isPaginationTextVisible: false }} />
      </div>
    </>
  );
}

export default TransactionList;
