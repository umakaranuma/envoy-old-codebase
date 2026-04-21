import Table from '@/components/table-properties/Table';
import { useTrans } from '@/helpers/services/lang/langService';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import React, { useEffect, useMemo } from 'react';
import { fetchTeamTableData } from '../_utils/services';
import { IFormData } from '../_utils/model';
import { thousandSeparator } from '@/helpers/services/commonService';
import ProfileInfo from '@/components/others/page-related/ProfileInfo';
import { getCurrency } from '@/helpers/services/currencyService';

function NativeTeamUserList({
  currentTeamId,
  setIsRCommissionEditVisible,
  setCurrentTeamMemberId,
  setCurrentTeamId,
  formData,
  currentIProductId,
}: {
  tableVers: number;
  setIsRCommissionEditVisible: any;
  setCurrentTeamMemberId: any;
  currentTeamId: string;
  setCurrentTeamId: Function;
  formData: IFormData[];
  currentIProductId: string;
}) {
  const t = useTrans('label.commission_setup,otr.common');
  const currency = getCurrency();

  useEffect(() => {
    setCurrentTeamId(currentTeamId);
  }, [currentTeamId]);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'display_name',
        header: t('member'),
        accessorKey: 'display_name',
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => {
          return <ProfileInfo title={cell.display_name} subtitle={cell.code} imageKey={cell.picture} />;
        },
      },
      {
        id: 'email',
        header: t('role'),
        accessorKey: 'email',
        cell: ({ cell }: { cell: any }) => cell.role_name || '-',
      },
      {
        id: 'id',
        header: t('commission'),
        accessorKey: 'id',
        cell: () => {
          const data = formData.find((item: IFormData) => String(item.id) === String(currentIProductId));
          const value = data?.commission_value;
          if (!data || !value) return <span>-</span>;
          const isPercentage = data?.commission_type === 'percentage';
          return isPercentage ? `${value}%` : `${currency.code} ${thousandSeparator(value)}`;
        },
      },
      {
        id: 'id',
        header: t('revised_commission'),
        accessorKey: 'id',
        align: 'right',
        cell: ({ cell }: { cell: any }) => {
          const data = formData.find((item: IFormData) => String(item.id) === String(currentIProductId));

          if (!data) return <span>-</span>;

          const revisedData = data.revised_commission_percent || [];
          const RcommssionData = revisedData.find((item: any) => item.team_id === currentTeamId && item.user_id === cell.id);
          return <span>{RcommssionData?.value ? (data.commission_type !== 'fixed' ? `${RcommssionData?.value}%` : `${currency.code} ${thousandSeparator(RcommssionData?.value ?? '')}`) : '-'}</span>;
        },
      },
      {
        header: t('action'),
        align: 'center',
        accessorKey: 'id',
        cell: ({ cell }: { cell: any }) => {
          return (
            <div
              className="clickable-text-primary"
              onClick={() => {
                setIsRCommissionEditVisible(true);
                setCurrentTeamMemberId(cell.getValue());
              }}
            >
              {t('edit')}
            </div>
          );
        },
      },
    ],
    [formData, currentIProductId],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: (props: any) => fetchTeamTableData({ ...props, teamId: currentTeamId }),
    paginate: true,
  });

  return <Table {...{ tableProperties, searchOption: false }} />;
}

export default NativeTeamUserList;
