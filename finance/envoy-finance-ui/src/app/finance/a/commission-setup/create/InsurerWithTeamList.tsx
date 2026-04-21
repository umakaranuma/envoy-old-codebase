import { ReactNode, useMemo } from 'react';
import { useTable } from '@apptimus-ui/table';
import { IFormData, IInsurerProduct } from '../_utils/model';
import { useTrans } from '@/helpers/services/lang/langService';
import { thousandSeparator } from '@/helpers/services/commonService';
import ProfileInfo from '@/components/others/page-related/ProfileInfo';
import { getCurrency } from '@/helpers/services/currencyService';

export default function InsurerWithTeamList({
  selectedInsurerProductData,
  // setIsRCommissionEditVisible,
  // setCurrentTeamMemberId,
  // setCurrentTeamId,
  // productGrpId,
  setIsAddCommissionVisible,
  setCurrentIProductId,
  formData,
  // teamUserTableVers,
  // salesTeamIds,
  // setSalesTeamIds
}: {
  selectedInsurerProductData: IInsurerProduct[];
  setIsRCommissionEditVisible: Function;
  setCurrentTeamMemberId: Function;
  setCurrentTeamId: Function;
  productGrpId: string;
  setIsAddCommissionVisible: Function;
  setCurrentIProductId: Function;
  formData: IFormData[];
  teamUserTableVers: number;
  salesTeamIds: string[];
  setSalesTeamIds: Function;
}) {
  const t = useTrans('label.commission_setup,otr.common');
  const data = selectedInsurerProductData;
  const currency = getCurrency();

  const columns = useMemo(
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
      {
        id: 'transaction_type',
        header: t('transaction_type'),
        accessorKey: 'transaction_type',
        cell: ({ cell }: { cell: any }) => {
          const data = formData.find((item: IFormData) => item.id === cell.id);
          return <div>{data?.transaction_type || '-'}</div>;
        },
      },
      {
        id: 'insurer',
        header: t('brokerage_revenue'),
        accessorKey: 'insurer',
        align: 'right',
        cell: ({ cell }: { cell: any }) => {
          const data = formData.find((item: IFormData) => item.id === cell.id);
          const value = data?.brokerage_commission_value;
          const isPercentage = data?.brokerage_commission_type === 'percentage';
          return isPercentage ? `${value}%` : `${currency.code} ${thousandSeparator(value ?? '')}`;
        },
      },
      {
        id: 'insurer',
        header: t('agent_commission'),
        accessorKey: 'insurer',
        align: 'right',
        cell: ({ cell }: { cell: any }) => {
          const data = formData.find((item: IFormData) => item.id === cell.id);
          const value = data?.commission_value || '';
          const isPercentage = data?.commission_type === 'percentage';
          return isPercentage ? `${value}%` : `${currency.code} ${thousandSeparator(value)}`;
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
                setIsAddCommissionVisible(true);
                setCurrentIProductId(cell.id);
              }}
            >
              {t('edit')}
            </div>
          );
        },
      },
    ],
    [],
  );

  const { Table } = useTable({
    columns: columns,
    data: data,
    // rowExpandable: {
    //   primaryKey: 'id',
    //   expandableRows: () => true,
    //   expandedRowRender: (record: any) => {
    //     return (
    //       <div className="">
    //         <ProductGroupTeamsList
    //           productGrpId={productGrpId}
    //           tableVers={0}
    //           setIsRCommissionEditVisible={setIsRCommissionEditVisible}
    //           setCurrentTeamMemberId={setCurrentTeamMemberId}
    //           setCurrentTeamId={setCurrentTeamId}
    //           currentInsurencerId={record?.id}
    //           setCurrentIProductId={setCurrentIProductId}
    //           formData={formData}
    //           teamUserTableVers={teamUserTableVers}
    //           setSalesTeamIds={setSalesTeamIds}
    //            salesTeamIds={salesTeamIds?.map(id => ({ id })) || []}
    //         />
    //       </div>
    //     );
    //   },
    // },
  });

  return <div className="p-3 mb-2 rounded bg-white">{Table as ReactNode}</div>;
}
