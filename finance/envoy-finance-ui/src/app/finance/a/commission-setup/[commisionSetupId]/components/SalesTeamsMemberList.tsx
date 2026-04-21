import Table from '@/components/table-properties/Table';
import { ITablePropertyColumn } from '@/interface/ICommon';
import { useAsyncTable } from '@apptimus-ui/table';
import { useEffect, useMemo } from 'react';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { fetchSalesTeamMemberTableData } from '../../_utils/services';
import { thousandSeparator } from '@/helpers/services/commonService';
import ProfileInfo from '@/components/others/page-related/ProfileInfo';
import { getCurrency } from '@/helpers/services/currencyService';

function SalesTeamsMemberList({
  currentTeamId,
  setIsRCommissionEditVisible,
  setEditTeamMemberId,
  setupId,
  setRCommisSionData,
  teamMemberTableVers,
  isEditForm,
  setCurrentTeamId,
}: {
  currentTeamId: string;
  setIsRCommissionEditVisible: Function;
  setEditTeamMemberId: Function;
  setupId: string;
  setRCommisSionData: any;
  teamMemberTableVers: number;
  isEditForm: boolean;
  setCurrentTeamId: Function;
}) {
  const t = useTrans('label.commission_setup,otr.common');
  const currency = getCurrency();
  useEffect(() => {
    setCurrentTeamId(currentTeamId);
  }, [currentTeamId]);

  const columns = useMemo<ITablePropertyColumn[]>(
    () => [
      {
        id: 'member',
        header: t('member'),
        accessorKey: 'member',
        visibilityLock: false,
        cell: ({ cell }: { cell: any }) => {
          return <ProfileInfo title={cell.display_name} subtitle={cell.code} imageKey={cell.picture} />;
        },
      },
      {
        id: 'role',
        header: t('role'),
        accessorKey: 'role',
        cell: ({ cell }: { cell: any }) => {
          return <>{cell.role_name || '-'}</>;
        },
      },
      {
        id: 'commission',
        header: t('commission'),
        accessorKey: 'commission',
        cell: ({ cell }: { cell: any }) => {
          const data = cell.agent_commission_percent.value;
          const isPercentage = cell?.agent_commission_percent.type !== 'fixed';
          return <> {cell.agent_commission_percent?.value ? <>{isPercentage ? `${data} %` : `${currency.code} ${thousandSeparator(data || '')}`}</> : 'N/A'} </>;
        },
      },
      {
        id: 'revised_commission',
        header: t('revised_commission'),
        accessorKey: 'revised_commission',
        align: 'right',
        cell: ({ cell }: { cell: any }) => {
          return (
            <span>
              {cell.revised_commission?.value ? (
                <>
                  {cell.revised_commission?.value && cell.revised_commission.type !== 'fixed'
                    ? `${cell.revised_commission?.value}%`
                    : `${currency.code} ${thousandSeparator(cell.revised_commission?.value)}`}
                </>
              ) : (
                'N/A'
              )}
            </span>
          );
        },
      },
      ...(isEditForm
        ? [
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
                      setEditTeamMemberId(cell.getValue());
                    }}
                  >
                    {t('revise')}
                  </div>
                );
              },
            },
          ]
        : []),
    ],
    [],
  );

  const tableProperties = useAsyncTable({
    columns: columns,
    loadData: async (params) => {
      const response = await fetchSalesTeamMemberTableData({ ...params, setupId: setupId, teamId: currentTeamId });
      if (response?.data) {
        const revisedMap: Record<string, string> = {};

        response.data.forEach((item: any) => {
          const key = `${currentTeamId}_${item.id}`;
          revisedMap[key] = item?.revised_commission?.value || '';
        });

        setRCommisSionData(revisedMap);
      }
      return response;
    },
    paginate: true,
  });

  useEffect(() => {
    tableProperties.reload();
  }, [teamMemberTableVers]);

  return (
    <>
      <div className={`data-table-container card custom-card mt-4}`}>
        <Table heading={<PageHeading title={t('job_titles')} icon="sun-light" />} {...{ tableProperties }} searchOption={false} />
      </div>
    </>
  );
}

export default SalesTeamsMemberList;
