import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useMemo } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams, useRouter } from 'next/navigation';
import { fetchAllPoliciesTableData } from '../../../services';
import S3Avatar from '@/components/others/page-related/S3Avatar';
import { useCurrency } from '@/contexts/CurrencyContext';
import { hexToRgba, thousandSeparator } from '@/helpers/services/commonService';

function PoliciesList() {
  const t = useTrans('label.sales_managements,otr.common');
  const params = useParams();
  const lead_id = params.managementId?.toString() || '';
  const { currency } = useCurrency();
  const router = useRouter();
  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'brokerage_policy_id',
        header: t('policy_number'),
        accessorKey: 'brokerage_policy_id',
        sort: true,
        cell: ({ cell }: any) => (
          <div className="clickable-text" onClick={() => router.push(`/policy/a/issued-policies/${cell.id}`)}>
            {cell.getValue()}
          </div>
        ),
      },
      {
        id: 'product_name',
        header: t('product_name'),
        accessorKey: 'product_name',
        sort: true,
      },
      // {
      //   id: 'risk_type',
      //   header: t('risk_type'),
      //   accessorKey: 'risk_type',
      //   sort: true,
      //   cell: ({ cell }: any) => <div>{cell.risk_types.map((type: any) => type.name).join(', ') || '-'}</div>,
      // },
      {
        id: 'sum_insured',
        header: `${t('sum_insured_amount')} (${currency.code})`,
        accessorKey: 'sum_insured',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'premium_amount',
        header: `${t('premium_amount')} (${currency.code})`,
        accessorKey: 'premium_amount',
        sort: true,
        align: 'right',
        cell: ({ cell }: { cell: any }) => <div className="amount-container">{thousandSeparator(cell.getValue()) || '-'}</div>,
      },
      {
        id: 'start_date',
        header: t('start_date'),
        accessorKey: 'start_date',
        sort: true,
      },
      {
        id: 'end_date',
        header: t('end_date'),
        accessorKey: 'end_date',
        sort: true,
      },
      {
        id: 'insurer',
        header: t('insurer'),
        accessorKey: 'insurer',
        sort: true,
        cell: ({ cell }: any) => (
          <div className="d-flex align-items-center gap-2">
            <div>
              <S3Avatar imageKey={undefined} width={20} height={20} />
              {cell.insurer_name}
            </div>
          </div>
        ),
      },
      {
        id: 'status_name',
        header: t('status'),
        accessorKey: 'status_name',
        sort: true,
        align: 'center',
        cell: ({ cell, onClick }: any) => {
          return (
            <div className="d-flex justify-content-between align-items-center gap-3" onClick={onClick}>
              <div
                className={`d-flex flex-row align-items-center text-capitalize gap-1 rounded-1 fs-10 fw-bold badge`}
                style={{ background: hexToRgba(cell.status_color, 0.1), border: `1px solid ${cell.status_color}`, color: `${cell.status_color}` }}
              >
                <svg width="9" height="8" viewBox="0 0 9 8" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="4.375" cy="4" r="3" fill={cell.status_color} />
                </svg>
                {cell.status_name}
              </div>
            </div>
          );
        },
      },
      // {
      //   id: 'remarks',
      //   header: t('remarks'),
      //   accessorKey: 'remarks',
      //   sort: true,
      //   cell: ({ cell }: any) => <div>{cell.getValue() || '-'}</div>,
      //   align: 'center',
      // },
      // {
      //   header: t('action'),
      //   align: 'center',
      //   accessorKey: 'id',
      //   cell: () => (
      //     <Dropdown
      //       trigger={
      //         <span className="action-icon">
      //           <Flexicon icon="dots-horizontal" variant="line" size={17} />
      //         </span>
      //       }
      //     >
      //       {(onClose: Function) => (
      //         <span className="t-action">
      //           <DropdownItem onClick={() => onClose()}>
      //             <span className="d-flex gap-2">
      //               <Flexicon icon="repeat-04" variant="line" size={17} />
      //               <span>{t('renewal')}</span>
      //             </span>
      //           </DropdownItem>
      //           <DropdownItem onClick={() => onClose()}>
      //             <span className="d-flex gap-2">
      //               <Flexicon icon="send-03" variant="line" size={17} />
      //               <span>{t('send')}</span>
      //             </span>
      //           </DropdownItem>
      //           <DropdownItem onClick={() => onClose()}>
      //             <span className="d-flex gap-2">
      //               <Flexicon icon="download-01" variant="line" size={17} />
      //               <span>{t('download')}</span>
      //             </span>
      //           </DropdownItem>
      //           <DropdownItem onClick={() => {}}>
      //             <span className="d-flex gap-2">
      //               <Flexicon icon="annotation-dots" variant="line" size={17} />
      //               <span>{t('send_reminder')}</span>
      //             </span>
      //           </DropdownItem>
      //         </span>
      //       )}
      //     </Dropdown>
      //   ),
      //   customizable: false,
      // },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchAllPoliciesTableData(props, lead_id),
    paginate: true,
  });

  return (
    <>
      <div className={`data-table-container card custom-card px-2`}>
        <Table heading={<PageHeading title={t('interaction')} />} searchOption={false} {...{ tableProperties }} />
      </div>
    </>
  );
}

export default PoliciesList;
