import { useMemo, useState } from 'react';
import { useAsyncTable } from '@apptimus-ui/table';
import { useTrans } from '@/helpers/services/lang/langService';
import SalesTeamsMemberList from './SalesTeamsMemberList';
import { thousandSeparator } from '@/helpers/services/commonService';
import Table from '@/components/table-properties/Table';
import { fetchNativeProductTeamTableData, fetchProductGroupTeamTableData } from '../../_utils/services';
import { getCurrency } from '@/helpers/services/currencyService';

export default function SalesTeamListEdit({
  defaultTeams,
  defaultCommissionValue,
  defaultCommissionType,
  setCurrentTeamId,
  setIsRCommissionEditVisible,
  setEditTeamMemberId,
  setupId,
  setRCommisSionData,
  teamMemberTableVers,
  isEditForm,
  productId,
  setSalesTeamIds,
  insurerId,
}: {
  defaultTeams?: any[];
  defaultCommissionValue: string;
  defaultCommissionType: string;
  setCurrentTeamId: Function;
  setIsRCommissionEditVisible: Function;
  setEditTeamMemberId: Function;
  setupId: string;
  setRCommisSionData: Function;
  teamMemberTableVers: number;
  isEditForm: boolean;
  productId: string;
  setSalesTeamIds: Function;
  insurerId: string;
}) {
  const t = useTrans('label.commission_setup,otr.common');
  const [defaultSelectedTeamIds, _setDefaultSelectedTeamIds] = useState<any[]>(defaultTeams || []);
  const currency = getCurrency();

  const columns = useMemo(
    () => [
      {
        id: 'name',
        header: t('team_name'),
        accessorKey: 'name',
        cell: ({ cell }: { cell: any }) => cell.getValue() || '-',
      },
      {
        id: 'agent_commission',
        header: t('agent_commission'),
        accessorKey: 'agent_commission',
        align: 'right',
        cell: () => {
          if (!defaultCommissionValue) return '-';
          return `${defaultCommissionType === 'fixed' ? `${currency.code} ${thousandSeparator(defaultCommissionValue)}` : `${defaultCommissionValue}%`}`;
        },
      },
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) =>
      insurerId !== ''
        ? fetchProductGroupTeamTableData({ ...props, productGrpId: productId, currentInsurencerId: insurerId })
        : fetchNativeProductTeamTableData({ ...props, nativeProductId: productId }),
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
      expandMode: 'single',
      expandableRows: () => true,
      expandedRowRender: (record: any) => {
        return (
          <div>
            <SalesTeamsMemberList
              currentTeamId={record.id}
              setEditTeamMemberId={setEditTeamMemberId}
              setIsRCommissionEditVisible={setIsRCommissionEditVisible}
              setupId={setupId}
              setRCommisSionData={setRCommisSionData}
              teamMemberTableVers={teamMemberTableVers}
              isEditForm={isEditForm}
              setCurrentTeamId={setCurrentTeamId}
              key={teamMemberTableVers}
            />
          </div>
        );
      },
    },
  });
  return <Table {...{ tableProperties, searchOption: false }} />;
}
