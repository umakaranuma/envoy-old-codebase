import { ReactNode, useMemo } from 'react';
import { useTable } from '@apptimus-ui/table';
import { useTrans } from '@/helpers/services/lang/langService';
import SalesTeamsMemberList from './SalesTeamsMemberList';
import { ITeam } from '../../_utils/model';
import { thousandSeparator } from '@/helpers/services/commonService';
import { getCurrency } from '@/helpers/services/currencyService';

export default function SalesTeamList({
  tableData,
  defaultCommissionValue,
  defaultCommissionType,
  setCurrentTeamId,
  setIsRCommissionEditVisible,
  setEditTeamMemberId,
  setupId,
  setRCommisSionData,
  teamMemberTableVers,
  isEditForm,
}: {
  tableData?: ITeam[];
  defaultCommissionValue: string;
  defaultCommissionType: string;
  setCurrentTeamId: Function;
  setIsRCommissionEditVisible: Function;
  setEditTeamMemberId: Function;
  setupId: string;
  setRCommisSionData: Function;
  teamMemberTableVers: number;
  isEditForm: boolean;
}) {
  const t = useTrans('label.commission_setup,otr.common');
  const data = tableData;
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
          return `${defaultCommissionType !== 'percentage' ? `${currency.code} ${thousandSeparator(defaultCommissionValue)}` : `${defaultCommissionValue}%`}`;
        },
      },
    ],
    [],
  );

  const { Table } = useTable({
    columns: columns,
    data: data,
    rowExpandable: {
      primaryKey: 'id',
      expandMode: 'single',
      expandableRows: () => true,
      expandedRowRender: (record) => {
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

  return <div className="p-3 mb-2 rounded bg-white">{Table as ReactNode}</div>;
}
