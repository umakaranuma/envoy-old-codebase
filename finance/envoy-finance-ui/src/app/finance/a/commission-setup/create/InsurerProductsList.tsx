import Table from '@/components/table-properties/Table';
import { useTrans } from '@/helpers/services/lang/langService';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import React, { useEffect, useMemo, useState } from 'react';
import { fetchInsurerProductsByNativeProductTableData } from '../_utils/services';
import { ICommon, IInsurerProduct } from '../_utils/model';
import ProfileInfo from '@/components/others/page-related/ProfileInfo';

function InsurerProductsList({
  tableVers,
  uiFormData,
  nativeProductId,
  selectedInsurerProductData,
  setSelectedInsurerProductData,
  setFormData,
}: {
  tableVers: number;
  nativeProductId: string | null;
  selectedInsurerProductData: any[];
  setSelectedInsurerProductData: Function;
  setFormData: Function;
  uiFormData: ICommon;
}) {
  const t = useTrans('label.commission_setup,otr.common');
  const [defaultInsurerData, _setDefaultInsurerData] = useState<any[]>(selectedInsurerProductData);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'name',
        header: t('product_name'),
        accessorKey: 'name',
        sort: true,
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'insurer',
        header: t('insurer_info'),
        accessorKey: 'insurer',
        sort: true,
        cell: ({ cell }: { cell: any }) => (
          <ProfileInfo imageKey={cell.insurer.logo} defaultImage="/images/default-profile.png" title={cell.insurer.name} subtitle={cell.insurer.email} shape="square" />
        ),
      },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchInsurerProductsByNativeProductTableData({ ...props, nativeProductId }),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'multiple',
      actionColumn: true,
      enableSelectAll: true,
      action: (_: any, data: any) => {
        setSelectedInsurerProductData(data);

        const selectedData = data.map((product: IInsurerProduct) => ({
          id: product.id,
          vendor_id: product.vendor_id,
          name: product.name,
          transaction_type: uiFormData.transaction_type,
          transaction_id: uiFormData.transaction_id,
          commission_type: uiFormData.commission_type,
          commission_value: uiFormData.commission_value,
          brokerage_commission_value: uiFormData.brokerage_commission_value,
          brokerage_commission_type: uiFormData.brokerage_commission_type,
          revised_commission_percent: [],
        }));

        setFormData(selectedData);
      },
      defaultSelectedKeys: defaultInsurerData,
    },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableVers, nativeProductId]);

  return <Table {...{ tableProperties, searchOption: false, isRowPerPageVisible: false }} />;
}

export default React.memo(InsurerProductsList);
