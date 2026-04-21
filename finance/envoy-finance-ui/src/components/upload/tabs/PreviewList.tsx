import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { UploadSummaryData } from '@/interface/model';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo, useState } from 'react';
// import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
// import { Flexicon } from '@apptimus-ui/flexicon';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchAllCommissionData } from '@/app/finance/a/commission-setup/_utils/services';
import { fetchAllPaymentData } from '@/app/finance/a/payments/_utils/services';

interface PreviewListProps {
  type: 'payments' | 'commission_setup';
  data: UploadSummaryData;
  onEdit: Function;
}

function PreviewList({ type }: PreviewListProps) {
  const t = useTrans('label.invoice,label.commission_setup,otr.common');
  const tableName = type === 'payments' ? 'payments' : 'commission_setup';
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);

  const columns = useMemo<ITablePropertyColumn[]>(() => {
    if (type === 'payments') {
      return [
        {
          id: 'invoice_no',
          header: t('invoice_no'),
          accessorKey: 'invoice_no',
          sort: true,
          visibilityLock: false,
        },
        {
          id: 'invoice_date',
          header: t('invoice_date'),
          accessorKey: 'invoice_date',
          sort: true,
        },
        {
          id: 'policy_info',
          header: t('policy_info'),
          accessorKey: 'policy_info',
          sort: true,
        },
        {
          id: 'insurer_info',
          header: t('insurer_info'),
          accessorKey: 'policy_info',
          sort: true,
        },
        {
          id: 'settled_amount',
          header: t('settled_amount'),
          accessorKey: 'settled_amount',
          sort: true,
        },
        {
          id: 'outstanding_amount',
          header: t('outstanding_amount'),
          accessorKey: 'outstanding_amount',
          sort: true,
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
        //           <DropdownItem onClick={() => (setIsFullscreen(false), onEdit(cell.getValue()), onClose())}>
        //             <span className="d-flex gap-2">
        //               <Flexicon icon="pencil-line" variant="line" size={17} />
        //               <span>{t('edit')}</span>
        //             </span>
        //           </DropdownItem>
        //         </span>
        //       )}
        //     </Dropdown>
        //   ),
        //   customizable: false,
        // },
      ];
    } else {
      return [
        {
          id: 'product_name',
          header: t('product_name'),
          accessorKey: 'product_name',
          sort: true,
          visibilityLock: false,
        },
        {
          id: 'insurer_name',
          header: t('insurer_info'),
          accessorKey: 'insurer_name',
          sort: true,
        },
        {
          id: 'transaction_type',
          header: t('transaction_type'),
          accessorKey: 'transaction_type',
          sort: true,
        },
        {
          id: 'team_name',
          header: t('sales_team'),
          accessorKey: 'team_name',
          sort: true,
        },
        {
          id: 'brokerage_revenue_percent',
          header: t('brokerage_revenue'),
          accessorKey: 'brokerage_revenue_percent',
          sort: true,
        },
        {
          id: 'agent_commission_percent',
          header: t('agent_commission'),
          accessorKey: 'agent_commission_percent',
          sort: true,
        },
        // {
        //   id: 'bonus_commission_percent',
        //   header: t('bonus_commission_percent'),
        //   accessorKey: 'bonus_commission_percent',
        //   sort: true,
        // },
        // {
        //   id: 'target_achievement_commission_percent',
        //   header: t('target_achievement_commission'),
        //   accessorKey: 'target_achievement_commission_percent',
        //   sort: true,
        // },
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
        //           <DropdownItem onClick={() => (setIsFullscreen(false), onEdit(cell.getValue()), onClose())}>
        //             <span className="d-flex gap-2">
        //               <Flexicon icon="pencil-line" variant="line" size={17} />
        //               <span>{t('edit')}</span>
        //             </span>
        //           </DropdownItem>
        //         </span>
        //       )}
        //     </Dropdown>
        //   ),
        //   customizable: false,
        // },
      ];
    }
  }, [type, t]);

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: type === 'payments' ? fetchAllPaymentData : fetchAllCommissionData,
    paginate: true,
    rowSelection: false,
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableColumnVers, type]);

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
        <Table
          heading={<PageHeading title={t(type === 'payments' ? 'payments' : 'commission_setup')} icon="sun-light" />}
          {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible }}
        />
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

export default PreviewList;
