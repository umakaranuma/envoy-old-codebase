import { useEffect, useMemo, useState } from 'react';
import Table from '@/components/table-properties/Table';
import { useTrans } from '@/helpers/services/lang/langService';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import DeleteConfirmPop from '@/components/others/DeleteConfirmPop';
import { CustomizeColumn, useCustomizeColumn } from '@/components/others/CustomizeColumn';
import { fetchInsurerProductsByNativeProductTableData } from '../../services';
import { useRouter } from 'next/navigation';
import ProfileInfo from '@/components/others/page-related/ProfileInfo';

const InsureProductList = ({
  nativeProductId,
  tableVers,
  isEdit = false,
  handleOnDelete,
  tableColumnVers,
  setTableColumnVers,
}: {
  nativeProductId: string;
  tableVers: number;
  isEdit: boolean;
  handleOnDelete?: Function;
  tableColumnVers?: number;
  setTableColumnVers?: Function;
}) => {
  const t = useTrans('label.products,otr.common');
  const tableName = 'native-product-insurers';
  const router = useRouter();
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [isCustColumnVisible, setIsCustColumnVisible] = useState(false);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'code',
        header: t('product_code'),
        accessorKey: 'code',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => (
          <div className="clickable-text" onClick={() => router.push(`/a/products/insurer-product/${cell.id}`)}>
            {cell.code}
          </div>
        ),
      },
      {
        id: 'name',
        header: t('insurer_product_name'),
        accessorKey: 'name',
        sort: true,
      },
      {
        id: 'insurer',
        header: t('insurer'),
        accessorKey: 'insurer',
        sort: true,
        cell: ({ cell }: { cell: any }) => (
          <div>
            <ProfileInfo imageKey={cell.insurer.logo} width={30} height={30} title={cell.insurer.name} shape="square" defaultImage="/images/default-profile.png" subtitle={cell.insurer.email} />
          </div>
        ),
      },
      // {
      //   id: 'type',
      //   header: t('risk_type'),
      //   accessorKey: 'type',
      //   sort: true,
      // },
      // {
      //   id: 'coverage_level',
      //   header: t('coverage_level'),
      //   accessorKey: 'coverage_level',
      //   sort: true,
      // },
      {
        id: 'description',
        header: t('description'),
        accessorKey: 'description',
        sort: true,
      },
      ...(isEdit
        ? [
            {
              id: 'actions',
              header: t('action'),
              align: 'center',
              accessorKey: 'id',
              cell: ({ cell }: { cell: any }) => (
                <DeleteConfirmPop trigger={<div className="text-primary pointer fw-semibold">unmap</div>} deleteId={cell.getValue()} handleOnDelete={handleOnDelete ?? (() => {})} onClose={() => {}} />
              ),
            },
          ]
        : []),
    ],
    [tableVers, isEdit],
  );

  const tableColumns = useCustomizeColumn({ ...{ tableName, columns, tableColumnVers } });

  const tableProperties = useAsyncTable({
    columns: tableColumns,
    loadData: (props: any) => fetchInsurerProductsByNativeProductTableData({ ...props, nativeProductId }),
    paginate: true,
    rowSelection: false,
  });

  useEffect(() => {
    if (nativeProductId) {
      tableProperties.reload();
    }
  }, [tableColumnVers, tableVers, nativeProductId]);
  return (
    <>
      <div className={`p-0 card custom-card ${isFullscreen ? 'dtc-fullscreen card-fullscreen' : 'mt-3'}`}>
        <Table {...{ tableProperties, isFullscreen, setIsFullscreen, setIsCustColumnVisible, searchOption: false, enableTopContent: false }} />
      </div>
      <CustomizeColumn
        key={tableColumnVers}
        isOpen={isCustColumnVisible}
        tableName={tableName}
        columns={tableColumns}
        onClose={() => setIsCustColumnVisible(false)}
        afterUpdate={() => setTableColumnVers?.((prevTableColumnVers: number) => prevTableColumnVers + 1)}
      />
    </>
  );
};

export default InsureProductList;
