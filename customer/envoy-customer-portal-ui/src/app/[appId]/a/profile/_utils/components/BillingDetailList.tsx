import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useMemo } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { formatDate, hexToRgba } from '@/helpers/services/commonService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { fetchPaymentListTableData } from '../services';
import { fileReceiver } from '@/helpers/services/storageService';

function BillingDetailList({ selectedIds, selectedFiles }: { selectedIds: (value: any) => void; selectedFiles: (value: any) => void }) {
  const t = useTrans('label.profile,otr.common');

  const handleFileViewer = async (key: string) => {
    const file = await fileReceiver({ key });
    window.open(file);
  };

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'invoice_number',
        header: t('debit_note'),
        accessorKey: 'invoice_number',
        visibilityLock: false,
        sort: true,
      },
      {
        id: 'paid_amount',
        header: t('amount'),
        accessorKey: 'paid_amount',
      },
      {
        id: 'created_at',
        header: t('date'),
        accessorKey: 'created_at',
        cell: ({ cell }: { cell: any }) => <div>{formatDate(cell.created_at ? cell.created_at : '')}</div>,
      },
      {
        id: 'status',
        header: t('status'),
        accessorKey: 'status',
        cell: ({ cell, onClick }: any) => {
          return (
            <div
              className={`rounded-5 fw-semibold badge`}
              style={{
                background: hexToRgba(cell.policy_request_status_color ? cell.policy_request_status_color : '', 0.1),
                border: `1px solid ${hexToRgba(cell.policy_request_status_color ? cell.policy_request_status_color : '', 0.4)}`,
                color: cell.policy_request_status_color ? cell.policy_request_status_color : '',
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
        id: 'receipt',
        header: t('action'),
        accessorKey: 'receipt',
        cell: ({ cell }: { cell: any }) => <Flexicon icon="download-cloud-02" className="action-icon" variant="line" size={28} onClick={() => handleFileViewer(cell.receipt)} />,
        align: 'center',
      },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchPaymentListTableData(props),
    paginate: true,
    rowSelection: false,
    rowSelectionProp: {
      key: 'id',
      mode: 'multiple',
      actionColumn: true,
      enableSelectAll: true,
      action: (value: any, data: any) => {
        selectedFiles(data.map((item: any) => item.receipt));
        selectedIds(value);
      },
    },
  });

  // useEffect(() => {
  //   tableProperties.reload();
  //   tableProperties.reset({ type: 'row-selection' });
  // }, []);

  return (
    <>
      <div className={`px-1 mt-3 py-3`}>
        <Table {...{ tableProperties, searchOption: false, isPaginationTextVisible: false }} />
      </div>
    </>
  );
}

export default BillingDetailList;
