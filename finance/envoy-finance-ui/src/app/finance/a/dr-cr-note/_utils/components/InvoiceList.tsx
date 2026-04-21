import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import { fetchInvoiceTableData } from '../service';
import { useRouter } from 'next/navigation';
import { formatDate, thousandSeparator } from '@/helpers/services/commonService';
import { getCurrency } from '@/helpers/services/currencyService';
import InvoiceType from './InvoiceType';

function InvoicesList({ onView, tableVers }: { onView: Function; tableVers: number }) {
  const t = useTrans('label.invoice,otr.common');
  const tableName = 'Invoices';
  const currency = getCurrency();
  const [tableColumnVers, _setTableColumnVers] = useState(0);
  const [_filterComKey, setFilterComKey] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableVersion, setTableVersion] = useState(0);

  const router = useRouter();
  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'invoice_number',
        header: t('dr_cr_note_number'),
        accessorKey: 'invoice_number',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'invoice_type',
        header: t('type'),
        accessorKey: 'invoice_type',
        sort: true,
        cell: ({ cell }: any) => {
          const value = cell.getValue();
          return <InvoiceType type={value} />;
        },
      },
      {
        id: 'created_by',
        header: t('agent_id'),
        accessorKey: 'created_by',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'insurer_info_full_name',
        header: t('insurer_info_full_name'),
        accessorKey: 'insurer_info_full_name',
        sort: true,
        cell: ({ cell }: { cell: any }) => (
          <span className="table-single-line" title={cell.getValue()}>
            {cell.getValue() || '-'}
            {cell.insurer_policy_id ? ` (ID: ${cell.insurer_policy_id})` : ''}
          </span>
        ),
      },
      // {
      //   id: 'insurer_policy_id',
      //   header: t('insurer_policy_id'),
      //   accessorKey: 'insurer_policy_id',
      //   sort: true,
      //   cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      // },
      {
        id: 'brokerage_policy_id',
        header: t('insurer_policy_number'),
        accessorKey: 'brokerage_policy_id',
        sort: true,
        cell: ({ cell }: { cell: any }) => {
          return (
            <div
              className="clickable-text-primary"
              onClick={() => {
                router.push(`/policy/a/issued-policies/${cell?.issued_policy_id}`);
              }}
            >
              {cell.getValue()}
            </div>
          );
        },
      },
      // {
      //   id: 'policy_number',
      //   header: t('policy_number'),
      //   accessorKey: 'policy_number',
      //   sort: true,
      //   cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      // },
      {
        id: 'endorsement_id',
        header: t('endorsement_id'),
        accessorKey: 'endorsement_id',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'invoice_date',
        header: t('dr_cr_note_date'),
        accessorKey: 'invoice_date',
        sort: true,
        cell: ({ cell }: { cell: any }) => formatDate(cell.getValue()) || '-',
      },
      {
        id: 'invoice_amount',
        header: `${t('dr_cr_note_amount')} (${currency.code})`,
        accessorKey: 'invoice_amount',
        align: 'right',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'paid_amount',
        header: `${t('paid_amount')} (${currency.code})`,
        accessorKey: 'paid_amount',
        align: 'right',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      // {
      //   id: 'last_paid_date',
      //   header: t('last_paid_date'),
      //   accessorKey: 'last_paid_date',
      //   sort: true,
      //   cell: ({ cell }: { cell: any }) => formatDate(cell.getValue()) || '-',
      // },
      {
        id: 'due_date',
        header: t('due_date'),
        accessorKey: 'due_date',
        sort: true,
        cell: ({ cell }: { cell: any }) => formatDate(cell.getValue()) || '-',
      },
      // {
      //   id: 'credit_age_days',
      //   header: t('credit_age_days'),
      //   accessorKey: 'credit_age_days',
      //   sort: true,
      //   align: 'right',
      //   cell: ({ cell }: { cell: any }) => cell.getValue() || '0',
      // },
      // {
      //   id: 'credit_period_days',
      //   header: t('credit_period_days'),
      //   accessorKey: 'credit_period_days',
      //   sort: true,
      //   align: 'right',
      //   cell: ({ cell }: { cell: any }) => cell.getValue() || '0',
      // },
      {
        id: 'outstanding_amount',
        header: `${t('outstanding_amount')} (${currency.code})`,
        accessorKey: 'outstanding_amount',
        align: 'right',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      // {
      //   id: 'remarks',
      //   header: t('remarks'),
      //   accessorKey: 'remarks',
      //   sort: true,
      // },
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
                <DropdownItem onClick={() => (onView(cell.getValue()), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="eye" variant="line" size={17} />
                    <span>{t('view')}</span>
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
    loadData: (props: any) => fetchInvoiceTableData(props),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
      enableSelectAll: true,
      action: (selectedId: string) => router.push(`/finance/a/dr-cr-note/${selectedId}`),
    },
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

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
        <Table
          heading={<PageHeading title={t('invoices')} icon="sun-light" />}
          searchOption={true}
          isRowPerPageVisible={false}
          {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible }}
        />
      </div>
      <CustomizeColumn
        key={tableVersion}
        isOpen={isCustColumnVisible}
        tableName={tableName}
        columns={tableColumns}
        onClose={() => setIsCustColumnVisible(false)}
        afterUpdate={() => setTableVersion((prev) => prev + 1)}
      />
    </>
  );
}

export default InvoicesList;
