import Table from '@/components/table-properties/Table';
import { useTrans } from '@/helpers/services/lang/langService';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import React, { useEffect, useMemo, useState } from 'react';
import { fetchProductGrpInsurerTableData } from '../_utils/services';
import { ICommon } from '../_utils/model';
import ProfileInfo from '@/components/others/page-related/ProfileInfo';

function InsurerList({
  tableVers,
  uiFormData,
  productGrpId,
  setSelectedInsurerData,
  setFormData,
  selectedInsurerData,
}: {
  tableVers: number;
  productGrpId: string | null;
  setSelectedInsurerData: Function;
  setFormData: Function;
  uiFormData: ICommon;
  selectedInsurerData: any[];
}) {
  const t = useTrans('label.commission_setup,otr.common');
  const [defaultInsurerData, _setDefaultInsurerData] = useState<any[]>(selectedInsurerData);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'insurer',
        header: t('insurer_info'),
        accessorKey: 'insurer',
        sort: true,
        cell: ({ cell }: { cell: any }) => {
          return <ProfileInfo title={cell.name} imageKey={cell.logo} />;
        },
      },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchProductGrpInsurerTableData({ ...props, productGrpId }),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'multiple',
      actionColumn: true,
      enableSelectAll: true,
      action: (_: any, data: any) => {
        setSelectedInsurerData(data);

        const selectedData = data.map((product: any) => ({
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
  }, [tableVers, productGrpId]);

  return <Table {...{ tableProperties, searchOption: false, isRowPerPageVisible: false }} />;
}

export default InsurerList;
