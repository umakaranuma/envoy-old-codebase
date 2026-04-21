import React, { useEffect, useMemo, useState } from 'react';
import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import Table from '@/components/table-properties/Table';
import { filterReducer } from '@/helpers/services/dataReducer';
import { fetchJournalEntriesTableData } from '../../service';
import { formatDate, thousandSeparator } from '@/helpers/services/commonService';
import { getCurrency } from '@/helpers/services/currencyService';

function ChartOfAccountsList({ tableVers }: { tableVers: number; onView: Function; onEdit: Function; handleOnDelete: Function }) {
  const t = useTrans('label.general_ledger,otr.common');
  const tableName = 'journal entries';
  const currency = getCurrency();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const [_filterComKey, setFilterComKey] = useState(0);
  const [_isFilterVisible, setIsFilterVisible] = useState(false);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'entry_number',
        header: t('entry_no'),
        accessorKey: 'entry_number',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'date',
        header: t('date'),
        accessorKey: 'date',
        sort: true,
        cell: ({ cell }: { cell: any }) => <>{formatDate(cell.date) || '-'}</>,
      },
      {
        id: 'account_name',
        header: t('account_name'),
        accessorKey: 'account_name',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },

      {
        id: 'debit_amount',
        header: `${t('debit_amount')} (${currency.code})`,
        accessorKey: 'debit_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'credit_amount',
        header: `${t('credit_amount')} (${currency.code})`,
        accessorKey: 'credit_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'description',
        header: t('transaction'),
        accessorKey: 'description',
        sort: true,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      // {
      //   header: t('action'),
      //   align: 'center',
      //   accessorKey: 'id',
      //   cell: ({ cell }: { cell: any }) => (
      //     <Dropdown
      //       trigger={
      //         <span className="action-icon">
      //           <Flexicon icon="dots-horizontal" variant="line" size={17} />
      //         </span>
      //       }
      //     >
      //       {(onClose: Function) => (
      //         <span className="t-action">
      //           <DropdownItem onClick={() => (setIsFullscreen(false), onView(cell.getValue()), onClose())}>
      //             <span className="d-flex gap-2">
      //               <Flexicon icon="eye" variant="line" size={17} />
      //               <span>{t('view')}</span>
      //             </span>
      //           </DropdownItem>
      //           <DropdownItem onClick={() => (setIsFullscreen(false), onEdit(cell.getValue()), onClose())}>
      //             <span className="d-flex gap-2">
      //               <Flexicon icon="pencil-line" variant="line" size={17} />
      //               <span>{t('edit')}</span>
      //             </span>
      //           </DropdownItem>
      //           <DeleteConfirmPop
      //             trigger={
      //               <DropdownItem onClick={() => null}>
      //                 <span className="d-flex gap-2 w-100">
      //                   <Flexicon icon="trash-03" variant="line" size={17} />
      //                   <span>{t('delete')}</span>
      //                 </span>
      //               </DropdownItem>
      //             }
      //             deleteId={cell.id}
      //             {...{ handleOnDelete, onClose }}
      //           />
      //         </span>
      //       )}
      //     </Dropdown>
      //   ),
      //   customizable: false,
      // },
    ],
    [],
  );

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: fetchJournalEntriesTableData,
    paginate: true,
    rowSelection: false,
    // rowSelectionProp: {
    //   key: 'id',
    //   mode: 'multiple',
    //   actionColumn: true,
    //   enableSelectAll: true,
    //   action: (selectedId: string) => onView(selectedId),
    // },
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
        <Table heading={<PageHeading title={t('reason')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible, setIsFilterVisible }} />
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

export default ChartOfAccountsList;
