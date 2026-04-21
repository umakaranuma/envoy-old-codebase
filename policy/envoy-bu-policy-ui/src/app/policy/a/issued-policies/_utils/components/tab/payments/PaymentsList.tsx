import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchPaymentTableData } from '../../../service';
import { useParams } from 'next/navigation';
import { formatDate, thousandSeparator } from '@/helpers/services/commonService';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import FileDownloadButton from '@/components/others/page-related/uploader/FileDownloadButton';
import { getCurrency } from '@/helpers/services/currencyService';

function PaymentsList({ onUploadReceipt, tableVersion }: { onUploadReceipt: (id: string) => void; tableVersion: number }) {
  const t = useTrans('label.issued_policies,otr.common');
  const params = useParams();
  const policyId = params.policyId?.toString() || '';
  const currency = getCurrency();

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'invoice_code',
        header: t('debit_note_number'),
        accessorKey: 'invoice_code',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'payment_created_at',
        header: t('date'),
        accessorKey: 'payment_created_at',
        sort: true,
        cell: ({ cell }: { cell: any }) => <>{formatDate(cell.payment_created_at)}</>,
      },
      {
        id: 'total_amount',
        header: `${t('debit_note_amount')} (${currency.code})`,
        accessorKey: 'total_amount',
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
      //   id: 'outstanding_amount',
      //   header: t('outstanding_amount'),
      //   accessorKey: 'outstanding_amount',
      //   sort: true,
      // },
      {
        id: 'doc_name',
        header: t('payment_receipt'),
        accessorKey: 'doc_name',
        sort: true,
        cell: ({ cell }: { cell: any }) => <>{cell.doc_name ? <FileDownloadButton s3Key={cell.doc} fileType="pdf" /> : '-'}</>,
      },
      {
        id: 'confirmation_payment_receipt_url',
        header: t('confirmation_receipt'),
        accessorKey: 'confirmation_payment_receipt_url',
        sort: true,
        align: 'center',
        cell: ({ cell }: { cell: any }) => <>{cell.confirmation_payment_receipt_url ? <FileDownloadButton s3Key={cell.confirmation_payment_receipt_url} fileType="pdf" /> : '-'}</>,
      },
      {
        id: 'remarks',
        header: t('remarks'),
        accessorKey: 'remarks',
        sort: true,
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
                <DropdownItem onClick={() => (onUploadReceipt(cell.getValue()), onClose())}>
                  <span className="d-flex gap-2">
                    <span>{t('upload_receipt')}</span>
                  </span>
                </DropdownItem>
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
    loadData: (props: any) => fetchPaymentTableData(props, policyId),
    paginate: true,
    rowSelection: false,
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableVersion]);

  return <Table searchOption={false} isRowPerPageVisible={false} {...{ tableProperties }} />;
}

export default PaymentsList;
