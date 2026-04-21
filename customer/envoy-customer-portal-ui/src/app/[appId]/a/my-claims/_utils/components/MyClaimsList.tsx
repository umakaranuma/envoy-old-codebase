import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useMemo } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchClaimsTableData } from '../service';
import { formatDate, hexToRgba } from '@/helpers/services/commonService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useParams, useRouter } from 'next/navigation';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';

function MyClaimsList({ onView }: { onView: Function }) {
  const t = useTrans('label.my_claims,otr.common');
  const router = useRouter();
  const params = useParams();
  const appId = params.appId as string;

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'code',
        header: t('claim_code'),
        accessorKey: 'code',
        sort: true,
      },
      {
        id: 'product_name',
        header: t('product_name'),
        accessorKey: 'product_name',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'created_at',
        header: t('request_date'),
        accessorKey: 'created_at',
        sort: true,
        cell: ({ cell }: any) => <>{formatDate(cell.created_at)}</>,
      },
      {
        id: 'brokerage_policy_id',
        header: t('policy_number'),
        accessorKey: 'brokerage_policy_id',
        sort: true,
      },
      {
        id: 'status_name',
        header: t('claim_status'),
        accessorKey: 'status_name',
        sort: true,
        visibilityLock: false,
        cell: ({ cell, onClick }: any) => {
          return (
            <div
              className={`rounded-5 fw-semibold badge`}
              style={{
                background: hexToRgba(cell.status_color ? cell.status_color : '', 0.1),
                border: `1px solid ${hexToRgba(cell.status_color ? cell.status_color : '', 0.4)}`,
                color: cell.status_color ? cell.status_color : '',
              }}
              onClick={onClick}
            >
              {cell.status_name}
            </div>
          );
        },
      },
      // {
      //   id: 'resolution_date',
      //   header: t('resolution_date'),
      //   accessorKey: 'resolution_date',
      //   sort: true,
      //   cell: ({ cell }: any) => <>{formatDate(cell.resolution_date)}</>,
      // },
      // {
      //   header: t('download'),
      //   align: 'center',
      //   accessorKey: 'id',
      //   cell: () => (
      //     <div className="action-icon">
      //       <Flexicon icon="download-cloud-01" variant="line" size={18} />
      //     </div>
      //   ),
      //   customizable: false,
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
                {/* <DropdownItem onClick={() => (onEdit(cell.getValue()), onClose())}>
                  <span className="d-flex gap-2">
                    <Flexicon icon="edit-05" variant="line" size={17} />
                    <span>{t('edit')}</span>
                  </span>
                </DropdownItem> */}
              </span>
            )}
          </Dropdown>
        ),
        customizable: false,
      },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchClaimsTableData(props),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'single',
      enableSelectAll: true,
      action: (selectedId: string) => router.push(`/${appId}/a/my-claims/${selectedId}`),
    },
  });

  return <Table {...{ tableProperties, searchOption: false }} />;
}

export default MyClaimsList;
