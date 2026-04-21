import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useMemo, useState } from 'react';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { useRouter } from 'next/navigation';
import { fetchIssuedPoliciesTableData } from '../service';
import { hexToRgba, thousandSeparator } from '@/helpers/services/commonService';
import { getCurrency } from '@/helpers/services/currencyService';
import ProfileInfo from '@/components/others/page-related/ProfileInfo';

function IssuedPoliciesList({ onView }: { onView: Function }) {
  const t = useTrans('label.issued_policies,otr.common');
  const currency = getCurrency();
  const tableName = 'issued_policies';
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);
  const [tableColumnVers, setTableColumnVers] = useState(0);
  const router = useRouter();

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'brokerage_policy_id',
        header: t('brokerage_policy_id'),
        accessorKey: 'brokerage_policy_id',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'customer_name',
        header: t('policyholder_info'),
        accessorKey: 'customer_name',
        sort: true,
      },
      {
        id: 'insurer_info_full_name',
        header: t('insurer_info'),
        accessorKey: 'insurer_info_full_name',
        sort: true,
        cell: ({ cell }: { cell: any }) => {
          return <ProfileInfo title={cell.insurer_info_full_name} subtitle={`${cell.risk_type_name}`} imageKey={cell.insurer_info_logo} defaultImage="/images/default-profile.png" shape="square" />;
        },
      },
      // {
      //   id: 'name',
      //   header: t('quotation_document'),
      //   accessorKey: 'name',
      //   sort: true,
      //   isHidden: true,
      // },
      // {
      //   id: 'invoice_document_name',
      //   header: t('invoice_document'),
      //   accessorKey: 'invoice_document_name',
      //   sort: true,
      //   cell: ({ cell }: { cell: any }) => <FileDownloadButton s3Key={cell.invoice_document} fileType="pdf" />,
      //   isHidden: true,
      // },
      // {
      //   id: 'policy_document',
      //   header: t('policy_document'),
      //   accessorKey: 'policy_document',
      //   sort: true,
      //   cell: ({ cell }: { cell: any }) => <FileDownloadButton s3Key={cell.policy_document} fileType="pdf" />,
      //   isHidden: true,
      // },
      // {
      //   id: 'sum_insured',
      //   header: `${t('sum_insured')} (${currency.code})`,
      //   accessorKey: 'sum_insured',
      //   sort: true,
      //   align: 'right',
      //   cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      //   isHidden: true,
      // },
      {
        id: 'premium_amount',
        header: `${t('premium_amount')} (${currency.code})`,
        accessorKey: 'premium_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      // {
      //   id: 'credit_period_days',
      //   header: t('credit_period'),
      //   accessorKey: 'credit_period_days',
      //   sort: true,
      //   align: 'right',
      //   isHidden: true,
      // },
      {
        id: 'credit_age_days',
        header: t('credit_age'),
        accessorKey: 'credit_age_days',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{cell.getValue() || '-'}</div>,
      },
      {
        id: 'policy_request_status',
        header: t('status'),
        accessorKey: 'policy_request_status',
        sort: true,
        align: 'center',
        cell: ({ cell, onClick }: any) => (
          <div
            className="rounded-5 fw-semibold badge"
            style={{
              background: hexToRgba(cell.status?.color ? cell.status.color : '', 0.1),
              border: `1px solid ${hexToRgba(cell.status?.color ? cell.status.color : '', 0.4)}`,
              color: cell.status?.color ? cell.status.color : '',
            }}
            onClick={onClick}
          >
            {cell.status?.name}
          </div>
        ),
      },
      // {
      //   id: 'created_at',
      //   header: t('issue_date'),
      //   accessorKey: 'created_at',
      //   cell: ({ cell }: { cell: any }) => {
      //     const dateValue = cell.getValue();
      //     return dateValue ? <span>{formatDate(dateValue)}</span> : null;
      //   },
      //   sort: true,
      //   isHidden: true,
      // },
      // {
      //   id: 'start_date',
      //   header: t('policy_start_date'),
      //   accessorKey: 'start_date',
      //   cell: ({ cell }: { cell: any }) => {
      //     const dateValue = cell.getValue();
      //     return dateValue ? <span>{formatDate(dateValue)}</span> : null;
      //   },
      //   sort: true,
      //   isHidden: true,
      // },
      // {
      //   id: 'end_date',
      //   header: t('policy_end_date'),
      //   accessorKey: 'end_date',
      //   cell: ({ cell }: { cell: any }) => {
      //     const dateValue = cell.getValue();
      //     return dateValue ? <span>{formatDate(dateValue)}</span> : null;
      //   },
      //   sort: true,
      //   isHidden: true,
      // },
      // {
      //   id: 'renewal_status',
      //   header: t('renewal_status'),
      //   accessorKey: 'renewal_status',
      //   sort: true,
      //   isHidden: true,
      // },
      // {
      //   id: 'remarks',
      //   header: t('remarks'),
      //   accessorKey: 'remarks',
      //   sort: true,
      //   isHidden: true,
      // },
      // {
      //   id: 'name',
      //   header: t('sales_agent'),
      //   accessorKey: 'name',
      //   sort: true,
      //   isHidden: true,
      // },
      // {
      //   id: 'name',
      //   header: t('account_manager'),
      //   accessorKey: 'name',
      //   sort: true,
      //   isHidden: true,
      // },
      // {
      //   id: 'created_by',
      //   header: t('added_by'),
      //   accessorKey: 'created_by',
      //   sort: true,
      //   isHidden: true,
      // },
      {
        id: 'pending_amount',
        header: `${t('pending_amount')} (${currency.code})`,
        accessorKey: 'pending_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'settled_amount',
        header: `${t('settled_amount')} (${currency.code})`,
        accessorKey: 'settled_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
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
                <DropdownItem onClick={() => (setIsFullscreen(false), onView(cell.getValue()), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="eye" variant="line" size={17} />
                    <span>{t('view')}</span>
                  </span>
                </DropdownItem>
                {/* <DropdownItem onClick={() => (setIsFullscreen(false), onView(cell.getValue()), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="pencil-line" variant="line" size={17} />
                    <span>{t('edit')}</span>
                  </span>
                </DropdownItem> */}
                {/* <DeleteConfirmPop
                  trigger={
                    <DropdownItem onClick={() => null}>
                      <span className="d-flex gap-2 w-100">
                        <Flexicon icon="trash-03" variant="line" size={17} />
                        <span>{t('delete')}</span>
                      </span>
                    </DropdownItem>
                  }
                  deleteId={cell.id}
                  {...{ handleOnDelete, onClose }}
                /> */}
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

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: (props: any) => fetchIssuedPoliciesTableData(props),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
      enableSelectAll: true,
      action: (selectedId: string) => router.push(`/policy/a/issued-policies/${selectedId}`),
    },
  });

  return (
    <>
      <div className={`data-table-container card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-4'}`}>
        <Table heading={<PageHeading title={t('policy_management')} icon="sun-light" />} {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible }} />
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

export default IssuedPoliciesList;
