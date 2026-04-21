import { useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchInvoiceTableData } from '../../../service';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useParams } from 'next/navigation';
import { formatDate, hexToRgba, thousandSeparator } from '@/helpers/services/commonService';
import { getCurrency } from '@/helpers/services/currencyService';
import { Badge } from '@apptimus-ui/ui-element';

function InvoicesList({ onView, tableVers }: { onView: Function; tableVers: number }) {
  const t = useTrans('label.issued_policies,otr.common');
  const tableName = 'channel';
  const [tableColumnVers, _setTableColumnVers] = useState(0);
  const [_filterComKey, setFilterComKey] = useState(0);
  const params = useParams();
  const policyId = params.policyId?.toString() || '';
  const currency = getCurrency();

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      // {
      //   id: 'broker_invoice_number',
      //   header: t('broker_invoice_number'),
      //   accessorKey: 'broker_invoice_number',
      //   sort: true,
      // },
      {
        id: 'invoice_number',
        header: t('dr_cr_note_id'),
        accessorKey: 'invoice_number',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'endorsement_code',
        header: t('endorsement_id'),
        accessorKey: 'endorsement_code',
        sort: true,
      },
      {
        id: 'transaction_type',
        header: t('transaction_type'),
        accessorKey: 'transaction_type',
        sort: true,
        cell: ({ cell }: any) => {
          return <div className="custom-primary-badge">{cell?.transaction_type?.name || '-'}</div>;
        },
      },
      {
        id: 'invoice_type',
        header: t('type'),
        accessorKey: 'invoice_type',
        sort: true,
        cell: ({ cell }: any) => {
          return (
            <Badge variant="outline" color={cell?.invoice_type === 'debit_note' ? 'danger' : 'success'}>
              {cell?.invoice_type === 'debit_note' ? 'DR' : 'CR'}
            </Badge>
          );
        },
      },
      {
        id: 'invoice_date',
        header: t('date'),
        accessorKey: 'invoice_date',
        sort: true,
        wrap: 'nowrap',
        cell: ({ cell }: { cell: any }) => <div className="text-nowrap">{formatDate(cell.getValue())}</div>,
      },
      {
        id: 'invoice_amount',
        header: `${t('dr_cr_note_amount')} (${currency.symbol})`,
        accessorKey: 'invoice_amount',
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
      {
        id: 'outstanding_amount',
        header: `${t('outstanding_amount')} (${currency.code})`,
        accessorKey: 'outstanding_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'invoice_status_name',
        header: t('status'),
        accessorKey: 'invoice_status_name',
        sort: true,
        align: 'center',
        cell: ({ cell, onClick }: any) => {
          return (
            <div
              className="rounded-5 fw-semibold badge"
              style={{
                background: hexToRgba(cell.invoice_status_color ? cell.invoice_status_color : '', 0.1),
                border: `1px solid ${hexToRgba(cell.invoice_status_color ? cell.invoice_status_color : '', 0.4)}`,
                color: cell.invoice_status_color ? cell.invoice_status_color : '',
              }}
              onClick={onClick}
            >
              {cell.invoice_status_name}
            </div>
          );
        },
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
          <>
            {cell.invoice_status_type !== 'payment_paid' && (
              <Dropdown
                trigger={
                  <span className="action-icon">
                    <Flexicon icon="dots-horizontal" variant="line" size={17} />
                  </span>
                }
              >
                {(onClose: Function) => (
                  <span className="t-action">
                    <DropdownItem onClick={() => (onView(cell.getValue()), onClose())}>
                      <span className="d-flex gap-2">
                        <span>{t('add_settlement')}</span>
                      </span>
                    </DropdownItem>
                  </span>
                )}
              </Dropdown>
            )}
          </>
        ),
        customizable: false,
      },
    ],
    [],
  );

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const reducer = (_state: any, action: any) => {
    if (action.isReset) {
      setFilterComKey((prevFilterComKey) => prevFilterComKey + 1);
    }

    return {
      filters: action.filterData,
    };
  };

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: (props: any) => fetchInvoiceTableData(props, policyId),
    paginate: true,
    rowSelection: false,
    customState: {
      initState: {
        filters: {},
      },
      reducer: reducer,
    },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers, tableVers]);

  return <Table searchOption={false} isRowPerPageVisible={false} {...{ tableProperties }} />;
}

export default InvoicesList;
