import { useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchAllVendorQuotationTableData } from '../../../../service';
import { formatDate, thousandSeparator } from '@/helpers/services/commonService';
import { useCurrency } from '@/contexts/CurrencyContext';

function ShortListedList({ tableVers, selectedIds, quotationId }: { tableVers: number; selectedIds: Function; quotationId: string }) {
  const t = useTrans('label.quotations,otr.common');
  const tableName = 'quotation_service_provider';
  const { currency } = useCurrency();
  const [tableColumnVers, _setTableColumnVers] = useState(0);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'service_provider_name',
        header: t('insurer_company_name'),
        accessorKey: 'service_provider_name',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'version',
        header: t('quotation_version'),
        accessorKey: 'version',
        sort: true,
      },
      {
        id: 'code',
        header: t('quotation_request_number'),
        accessorKey: 'code',
        sort: true,
      },
      {
        id: 'received_date',
        header: t('received_date'),
        accessorKey: 'received_date',
        sort: true,
        cell: ({ cell }: { cell: any }) => <div>{formatDate(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'total_amount',
        header: `${t('quotation_value')} (${currency.code})`,
        accessorKey: 'total_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'by_user_name',
        header: t('uploaded_by'),
        accessorKey: 'by_user_name',
        sort: true,
      },
      // {
      //     header: t('action'),
      //     align: 'center',
      //     accessorKey: 'id',
      //     cell: ({ cell }: { cell: any }) => (
      //         <Dropdown
      //             trigger={
      //                 <span className="action-icon">
      //                     <Flexicon icon="dots-horizontal" variant="line" size={17} />
      //                 </span>
      //             }
      //         >
      //             {(onClose: Function) => (
      //                 <span className="t-action">
      //                     <DropdownItem onClick={() => (onEdit(cell.getValue()), onClose())}>
      //                         <span className="d-flex gap-2">
      //                             <Flexicon icon="pencil-line" variant="line" size={17} />
      //                             <span>{t('edit')}</span>
      //                         </span>
      //                     </DropdownItem>
      //                 </span>
      //             )}
      //         </Dropdown>
      //     ),
      //     customizable: false,
      // },
    ],
    [],
  );

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: (props: any) => fetchAllVendorQuotationTableData(props, quotationId, 'shortlisted'),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'multiple',
      actionColumn: true,
      enableSelectAll: true,
      action: (value: any, _data: any) => {
        selectedIds(value);
      },
    },
  });

  useEffect(() => {
    tableProperties.reload();
    tableProperties.reset({ type: 'row-selection' });
  }, [tableColumnVers, tableVers]);

  return <Table heading={<PageHeading title={t('quotation_management')} icon="sun-light" />} {...{ tableProperties, searchOption: false, recordControl: false }} />;
}

export default ShortListedList;
