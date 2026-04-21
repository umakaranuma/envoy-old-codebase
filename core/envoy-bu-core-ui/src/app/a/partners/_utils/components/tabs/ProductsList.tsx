import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useMemo } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchPartnerProductTableData } from '../../service';
import { useRouter } from 'next/navigation';

function ProductsList({ partnerId }: { partnerId: string }) {
  const t = useTrans('label.partners,otr.common');
  const router = useRouter();
  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'code',
        header: t('code'),
        accessorKey: 'code',
        sort: true,
        cell: ({ cell }: { cell: any }) => (
          <div className="clickable-text" onClick={() => router.push(`/a/products/insurer-product/${cell.id}`)}>
            {cell.getValue()}
          </div>
        ),
      },
      {
        id: 'name',
        header: t('product_name'),
        accessorKey: 'name',
        sort: true,
        visibilityLock: false,
      },
      {
        id: 'partner_risk_type',
        header: t('partner_risk_type'),
        accessorKey: 'partner_risk_type',
        sort: true,
      },
      {
        id: 'native_risk_type',
        header: t('native_risk_type'),
        accessorKey: 'native_risk_type',
        sort: true,
      },
      // {
      //   id: 'account_name',
      //   header: t('account_name'),
      //   accessorKey: 'account_name',
      //   sort: true,
      //   visibilityLock: false,
      // },
      // {
      //   id: 'primary_contact',
      //   header: t('primary_contact'),
      //   accessorKey: 'primary_contact',
      //   sort: true,
      // },
      // {
      //   id: 'secondary_contact',
      //   header: t('secondary_contact'),
      //   accessorKey: 'secondary_contact',
      //   sort: true,
      // },
      // {
      //   id: 'description',
      //   header: t('description'),
      //   accessorKey: 'description',
      //   sort: true,
      //   cell: ({ cell }: { cell: any }) => (
      //     <div className="text-truncate" style={{ maxWidth: '100px' }}>
      //       {cell.description}
      //     </div>
      //   ),
      // },
      //   {
      //     header: t('action'),
      //     align: 'center',
      //     accessorKey: 'id',
      //     cell: ({ cell }: { cell: any }) => (
      //       <Dropdown
      //         trigger={
      //           <span className="action-icon">
      //             <Flexicon icon="dots-horizontal" variant="line" size={17} />
      //           </span>
      //         }
      //       >
      //         {(onClose: Function) => (
      //           <span className="t-action">
      //             <DropdownItem onClick={() => (setIsFullscreen(false), onView(cell.getValue()), onClose())}>
      //               <span className="d-flex gap-2">
      //                 <Flexicon icon="eye" variant="line" size={17} />
      //                 <span>{t('view')}</span>
      //               </span>
      //             </DropdownItem>
      //             <DropdownItem onClick={() => (setIsFullscreen(false), onEdit(cell.getValue()), onClose())}>
      //               <span className="d-flex gap-2">
      //                 <Flexicon icon="pencil-line" variant="line" size={17} />
      //                 <span>{t('edit')}</span>
      //               </span>
      //             </DropdownItem>
      //             <DeleteConfirmPop
      //               trigger={
      //                 <DropdownItem onClick={() => null}>
      //                   <span className="d-flex gap-2 w-100">
      //                     <Flexicon icon="trash-03" variant="line" size={17} />
      //                     <span>{t('delete')}</span>
      //                   </span>
      //                 </DropdownItem>
      //               }
      //               deleteId={cell.id}
      //               {...{ handleOnDelete, onClose }}
      //             />
      //           </span>
      //         )}
      //       </Dropdown>
      //     ),
      //     customizable: false,
      //   },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchPartnerProductTableData({ ...props, sp_id: partnerId }),
    paginate: true,
    rowSelection: false,
  });

  return (
    <>
      <div className={`data-table-container card custom-card mt-4`}>
        <Table {...{ tableProperties, searchOption: false }} />
      </div>
    </>
  );
}

export default ProductsList;
