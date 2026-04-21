import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useMemo } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchEndorsementTableData } from '../../service';
import { hexToRgba, thousandSeparator } from '@/helpers/services/commonService';
import Documents from './Documents';
import { getCurrency } from '@/helpers/services/currencyService';

function EndorsementsDetailsList({ policyId }: { policyId: string }) {
  const t = useTrans('label.issued_policies,otr.common');
  const currency = getCurrency();

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'endorsement_id',
        header: t('endorsement_id'),
        accessorKey: 'endorsement_id',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'endorsement_request_code',
        header: t('request_id'),
        accessorKey: 'endorsement_request_code',
        sort: true,
      },
      {
        id: 'endorsement_type_name',
        header: t('endorsement_type'),
        accessorKey: 'endorsement_type_name',
        sort: true,
      },
      {
        id: 'invoice_number',
        header: t('dr_cr_note_id'),
        accessorKey: 'invoice_number',
        sort: true,
      },
      {
        id: 'credit_period',
        header: t('credit_period'),
        accessorKey: 'credit_period',
        sort: true,
      },
      {
        id: 'invoice_status',
        header: t('status'),
        accessorKey: 'invoice_status_name',
        sort: true,
        cell: ({ cell, onClick }: any) => (
          <div
            className="rounded-5 fw-semibold badge"
            style={{ background: hexToRgba(cell.invoice_status_color || '', 0.1), border: `1px solid ${cell.invoice_status_color}`, color: cell.invoice_status_color }}
            onClick={onClick}
          >
            {cell.invoice_status_name}
          </div>
        ),
      },
      {
        id: 'cover_value',
        header: `${t('cover_value')} (${currency.code})`,
        accessorKey: 'cover_value',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'remarks',
        header: t('remarks'),
        accessorKey: 'remarks',
        sort: true,
        cell: ({ cell }: any) => <div>{cell.remarks || '-'}</div>,
      },
      {
        id: 'documents',
        header: t('documents'),
        accessorKey: 'documents',
        sort: true,
        align: 'center',
        cell: ({ cell }: { cell: any }) => {
          return (
            <div className="d-flex justify-content-center">
              <Documents endorsementsRequestId={cell.endorsement_request_id} endorsement_request_code={cell.endorsement_request_code} />
            </div>
          );
        },
      },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchEndorsementTableData(props, policyId),
    paginate: true,
    rowSelection: false,
  });

  return <Table searchOption={false} isRowPerPageVisible={false} {...{ tableProperties }} />;
}

export default EndorsementsDetailsList;
