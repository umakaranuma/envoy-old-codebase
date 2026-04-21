import PageHeading from '@/components/others/PageHeading';
import Table from '@/components/table-properties/Table';
import { useTrans } from '@/helpers/services/lang/langService';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import React, { useEffect, useMemo, useState } from 'react';
import { fetchProductGroupTeamTableData } from '../_utils/services';
import { IFormData } from '../_utils/model';
import NativeTeamUserList from './NativeTeamUserList';

function ProductGroupTeamsList({
  tableVers,
  productGrpId,
  setIsRCommissionEditVisible,
  setCurrentTeamId,
  setCurrentTeamMemberId,
  teamUserTableVers,
  currentInsurencerId,
  setCurrentIProductId,
  formData,
  salesTeamIds,
  setSalesTeamIds,
}: {
  tableVers?: number;
  productGrpId: string;
  setIsRCommissionEditVisible?: Function;
  setCurrentTeamId: Function;
  setCurrentTeamMemberId?: Function;
  teamUserTableVers: number;
  currentInsurencerId: number;
  setCurrentIProductId: Function;
  formData: IFormData[];
  salesTeamIds: any[];
  setSalesTeamIds: Function;
}) {
  const t = useTrans('label.commission_setup,otr.common');
  const [defaultSelectedTeamIds, _setDefaultSelectedTeamIds] = useState<any[]>(salesTeamIds || []);

  useEffect(() => {
    setCurrentIProductId(currentInsurencerId);
  }, [currentInsurencerId]);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'name',
        header: t('team_name'),
        accessorKey: 'name',
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchProductGroupTeamTableData({ ...props, productGrpId, currentInsurencerId }),
    paginate: true,
    rowSelection: true,
    rowSelectionProp: {
      key: 'id',
      mode: 'multiple',
      actionColumn: true,
      enableSelectAll: true,
      action: (value: any, _data: any) => {
        setSalesTeamIds(value);
      },
      defaultSelectedKeys: defaultSelectedTeamIds,
    },
    rowExpandable: {
      primaryKey: 'id',
      expandableRows: () => true,
      expandedRowRender: (record: any) => {
        return (
          <NativeTeamUserList
            currentTeamId={record?.id}
            tableVers={0}
            setIsRCommissionEditVisible={setIsRCommissionEditVisible}
            setCurrentTeamMemberId={setCurrentTeamMemberId}
            setCurrentTeamId={setCurrentTeamId}
            key={teamUserTableVers}
            formData={formData}
            currentIProductId={currentInsurencerId.toString()}
          />
        );
      },
    },
  });

  useEffect(() => {
    tableProperties.reload();
  }, [tableVers]);

  return (
    <>
      <div className={`data-table-container card custom-card mt-4`}>
        <Table heading={<PageHeading title={t('insurer_products')} icon="sun-light" />} {...{ tableProperties, searchOption: false }} />
      </div>
    </>
  );
}

export default ProductGroupTeamsList;
