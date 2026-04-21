import React, { useEffect, useMemo, useState } from 'react';
import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import Table from '@/components/table-properties/Table';
import { filterReducer } from '@/helpers/services/dataReducer';
import { fetchGeneralLedgerTableData } from '../../service';
import CustomBadge from '@/components/others/page-related/CustomBadge';
import { thousandSeparator } from '@/helpers/services/commonService';
import { getCurrency } from '@/helpers/services/currencyService';

function GeneralLedgerList({ tableVers }: { tableVers: number; onView: Function }) {
  const t = useTrans('label.general_ledger,otr.common');
  const tableName = 'general_ledger';
  const currency = getCurrency();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const [_filterComKey, setFilterComKey] = useState(0);
  const [_isFilterVisible, setIsFilterVisible] = useState(false);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      // {
      //   id: 'invoice_number',
      //   header: t('dr_cr_note'),
      //   accessorKey: 'invoice_number',
      //   sort: true,
      //   visibilityLock: false,
      //   cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      // },
      {
        id: 'insurer_name',
        header: t('insurer_info'),
        accessorKey: 'insurer_name',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'account_name',
        header: t('account_name'),
        accessorKey: 'account_name',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'account_number',
        header: t('account_number'),
        accessorKey: 'account_number',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'business_type_label',
        header: t('business_type_label'),
        accessorKey: 'business_type_label',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'total_debit',
        header: `${t('total_debit')} (${currency.code})`,
        accessorKey: 'total_debit',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'total_credit',
        header: `${t('total_credit')} (${currency.code})`,
        accessorKey: 'total_credit',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'ledger_status',
        header: t('ledger_status'),
        accessorKey: 'ledger_status',
        sort: true,
        cell: ({ cell }: { cell: any }) => {
          let badgeClass = '';
          const status = cell.total_debit >= 0 ? 'Processed' : 'pending';

          switch (status) {
            case 'Processed':
              badgeClass = 'success';
              break;
            case 'pending':
              badgeClass = 'warning';
              break;
            default:
              badgeClass = 'secondary';
          }
          return <CustomBadge text={status} color={badgeClass as any} />;
        },
      },
    ],
    [],
  );

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: fetchGeneralLedgerTableData,
    paginate: true,
    customState: {
      initState: {
        filters: {},
      },
      reducer: (_: any, action: any) => filterReducer({ action, setFilterComKey }),
    },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers, tableVers]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
        <Table heading={<PageHeading title={t('general_ledger')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible, setIsFilterVisible }} />
      </div>
      <CustomizeColumn
        key={tableColumnVers}
        isOpen={isCustColumnVisible}
        tableName={tableName}
        columns={tableColumns}
        onClose={() => setIsCustColumnVisible(false)}
        afterUpdate={() => setTableColumnVers((prevTableColumnVers) => prevTableColumnVers + 1)}
      />
    </>
  );
}

export default GeneralLedgerList;
