import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import Image from 'next/image';
import { Button } from '@apptimus-ui/ui-element';
import { SalesReportView } from './SalesReportView';
import { fetchSalesReportTableData } from '../../../_utils/service';

function SalesReportList({ tableVers, onView }: { tableVers: number; onView: Function }) {
  const t = useTrans('label.sales_report,otr.common');
  const tableName = 'payments';
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const [_filterComKey, setFilterComKey] = useState(0);
  const [isExportModalOpen, setIsExportModalOpen] = useState(false);
  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'payment_id',
        header: t('customer_name'),
        accessorKey: 'payment_id',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'invoice_no',
        header: t('transaction_date'),
        accessorKey: 'invoice_no',
        sort: true,
      },
      {
        id: 'payer_details',
        header: t('policy_name'),
        accessorKey: 'payer_details',
        sort: true,
      },
      {
        id: 'policy_info',
        header: t('policy_number'),
        accessorKey: 'policy_info',
        sort: true,
      },
      {
        id: 'amount_paid',
        header: t('paid_amount'),
        accessorKey: 'amount_paid',
        sort: true,
      },
      {
        id: 'payment_date',
        header: t('premium_amount'),
        accessorKey: 'payment_date',
        sort: true,
      },
      {
        id: 'transaction_type',
        header: t('total_amount'),
        accessorKey: 'transaction_type',
        sort: true,
      },
      {
        id: 'remarks',
        header: t('commission_amount'),
        accessorKey: 'remarks',
        sort: true,
      },
      {
        id: 'remarks',
        header: t('report_document'),
        accessorKey: 'remarks',
        cell: () => (
          <div className="gap-2 d-flex">
            <Image src={'/images/pdf.png'} alt="pdf" width={30} height={30} />
            <Image src={'/images/excel.png'} alt="pdf" width={30} height={30} />
          </div>
        ),
      },
      {
        header: t('action'),
        align: 'center',
        accessorKey: 'payment_id',
        cell: () => <Button variant="outline" text={'Export'} color={'light'} onClick={() => setIsExportModalOpen(true)} />,
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
    loadData: fetchSalesReportTableData,
    paginate: true,
    rowSelection: false,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
      action: (selectedId: string) => onView(selectedId),
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
        <Table heading={<PageHeading title={t('payments')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible }} />
      </div>
      <CustomizeColumn
        key={tableColumnVers}
        isOpen={isCustColumnVisible}
        tableName={tableName}
        columns={tableColumns}
        onClose={() => setIsCustColumnVisible(false)}
        afterUpdate={() => setTableColumnVers((prevTableColumnVers) => prevTableColumnVers + 1)}
      />
      <SalesReportView isOpen={isExportModalOpen} viewId={''} onClose={() => setIsExportModalOpen(false)} setEditId={() => {}} />
    </>
  );
}

export default SalesReportList;
