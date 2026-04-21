'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import React, { useEffect, useState } from 'react';
import { Button } from '@apptimus-ui/ui-element';
import { useParams, useRouter } from 'next/navigation';
import { toaster } from '@/helpers/services/toaster';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Description } from '@/components/others/Description';
import GoBack from '@/components/others/page-related/GoBack';
import { useBreadcrumb } from '@/contexts/BreadcrumbContext';
import { getCurrency } from '@/helpers/services/currencyService';
import { ICommissionData, initUIFormData, UIFormData } from '../../_utils/model';
import { formatCommissionValue } from '../../_utils/services';
import { getOneCommssionSetup, updateCommissionSetup, updateRCommission } from '../../_utils/api-service';
import SalesTeamListEdit from '../components/SalesTeamListEdit';
import EditRevisedCommission from '../components/RevisedCommission';

export default function Page() {
  const t = useTrans('label.commission_setup,label.mapping_data_table_preview,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const params = useParams();
  const viewId = params.commisionSetupId?.toString() || '';
  const router = useRouter();
  const { setCustomBreadcrumb } = useBreadcrumb();
  const currency = getCurrency();
  const [skeleton, setSkeleton] = useState(false);
  const [isEdit, setIsEdit] = useState(false);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState<ICommissionData | null>(null);
  const [uiFormData, setUiFormData] = useState<UIFormData>(initUIFormData);
  const [rCommissionEditVisible, setIsRCommissionEditVisible] = useState(false);
  const [editTeamMemberId, setEditTeamMemberId] = useState('');
  const [currentTeamId, setCurrentTeamId] = useState('');
  const [rCommisSionData, setRCommisSionData] = useState({});
  const [teamMemberTableVers, setTeamMemberTableVers] = useState(0);
  const [salesTeamIds, setSalesTeamIds] = useState<string[]>([]);
  // Helper function to format commission values using shared utility
  const formatValue = (value: number | string | undefined, type: string | undefined) => {
    return formatCommissionValue(value, type, currency.code);
  };

  useEffect(() => {
    setCustomBreadcrumb({
      text: t('view'),
      backurl: '/finance/a/commission-setup',
    });

    // cleanup on unmount
    return () => setCustomBreadcrumb(null);
  }, [setCustomBreadcrumb, formData]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setSkeleton(true);
        const responseData = await getOneCommssionSetup(viewId);
        if (responseData?.is_success) {
          const data = responseData.result;
          const transformedData: ICommissionData = {
            id: data.id.toString(),
            product_id: data.product_id,
            native_product_id: data.native_product_id,
            product_name: data.product_name,
            product_group_name: data.product_group_name,
            product_group_id: data.product_group_id,
            insurer: data.insurer,
            transaction_type: data.transaction_type.toString(),
            transaction_type_name: data.transaction_type_name,
            brokerage_revenue_percent: data.brokerage_revenue_percent,
            brokerage_revenue_type: data.commission_values.brokerage_revenue_percent[0]?.type,
            agent_commission_percent: data.agent_commission_percent,
            agent_commission_type: data.commission_values.agent_commission_percent[0]?.type,
            teams: data.teams,
          };
          setFormData(transformedData);
          setSalesTeamIds(data.teams.map((team: any) => team.id));
          const agentCommission = data.commission_values.agent_commission_percent?.[0] || {};
          const brokerageCommission = data.commission_values.brokerage_revenue_percent?.[0] || {};
          setUiFormData((prev) => ({
            ...prev,
            commission_type: agentCommission.type || '',
            commission_value: agentCommission.value || '',
            brokerage_commission_value: brokerageCommission.value || '',
            brokerage_commission_type: brokerageCommission.type || '',
          }));
        }
      } catch (error) {
        console.error(error);
      } finally {
        setSkeleton(false);
      }
    };

    if (viewId) {
      fetchData();
    }
  }, [viewId]);

  useEffect(() => {
    setTeamMemberTableVers((prev) => prev + 1);
  }, [isEdit]);

  // const onFormChange = (name: string, value: any) => {
  //     setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  // };

  function formatCommissionData(data: ICommissionData | null) {
    return {
      product_id: formData?.product_id,
      product_group_id: formData?.product_group_id,
      native_product_id: formData?.native_product_id,
      insurer_id: formData?.insurer.id,
      sales_team_ids: salesTeamIds,
      transaction_type: formData?.transaction_type,
      brokerage_revenue_percent: [
        {
          value: data?.brokerage_revenue_percent || '',
          type: data?.brokerage_revenue_type || '',
        },
      ],
      agent_commission_percent: [
        {
          value: data?.agent_commission_percent || '',
          type: data?.agent_commission_type || '',
        },
      ],
      commission_percent: [],
    };
  }

  const handleSubmit = async () => {
    setIsFormProcessing(true);
    const apiformData = formatCommissionData(formData);
    try {
      const responseData = await updateCommissionSetup(viewId, apiformData);
      setIsFormProcessing(false);
      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setTeamMemberTableVers((prev) => prev + 1);
        router.push('/finance/a/commission-setup');
        setIsEdit(false);
        setUiFormData((prev) => ({
          ...prev,
          brokerage_commission_value: formData?.brokerage_revenue_percent || '',
          brokerage_commission_type: formData?.brokerage_revenue_type || '',
          commission_value: formData?.agent_commission_percent || '',
          commission_type: formData?.agent_commission_type || '',
        }));
      }
      if (responseData.status_code === 417) {
        toaster.error(responseData.message);
      }
    } catch (error) {
      console.error('An error occurred:', error);
      setIsFormProcessing(false);
    }
  };

  function formatRCommissionData(data: any) {
    return Object.entries(data).map(([key, value]) => {
      const [, id] = key.split('_');
      return {
        id: parseInt(id),
        revised_commission: {
          value: value,
          type: formData?.agent_commission_type,
        },
      };
    });
  }

  async function onRCommissionEdit(data: any) {
    setIsFormProcessing(true);
    const apiRCommissionData = formatRCommissionData(data);
    try {
      const responseData = await updateRCommission(formData?.id as string, currentTeamId, apiRCommissionData);
      setIsFormProcessing(false);
      if (responseData.status_code === 417) {
        toaster.error(responseData.message);
      }
      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setIsRCommissionEditVisible(false);
        setTeamMemberTableVers((prev) => prev + 1);
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <div>
      <GoBack goTo={() => router.back()} title={t('commission_setup')} />
      <div className="panel">
        <div className="row gy-4 gx-4 mb-4">
          {formData?.product_name && (
            <div className="col-12 col-md-3">
              <Description label={t('product_name')} value={formData?.product_name} skeleton={skeleton} />
            </div>
          )}
          {formData?.product_group_name && (
            <div className="col-12 col-md-3">
              <Description label={t('product_group')} value={formData?.product_group_name} skeleton={skeleton} />
            </div>
          )}
          <div className="col-12 col-md-3">
            <Description label={t('transaction_type')} value={formData?.transaction_type_name} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-3">
            <Description label={t('brokerage_revenue')} value={formatValue(formData?.brokerage_revenue_percent, formData?.brokerage_revenue_type)} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-3">
            <Description label={t('agent_commission')} value={formatValue(formData?.agent_commission_percent, formData?.agent_commission_type)} skeleton={skeleton} />
          </div>
        </div>
        {formData && (
          <>
            <div className="panel-title">{t('sales_team_commissions')}</div>
            <div className=" rounded-4 mt-4 border border-1" key={teamMemberTableVers}>
              <SalesTeamListEdit
                teamMemberTableVers={teamMemberTableVers}
                setRCommisSionData={setRCommisSionData}
                setCurrentTeamId={setCurrentTeamId}
                setupId={formData?.id}
                setEditTeamMemberId={setEditTeamMemberId}
                setIsRCommissionEditVisible={setIsRCommissionEditVisible}
                isEditForm={true}
                defaultTeams={salesTeamIds.map((id: string) => ({ id }))}
                defaultCommissionValue={formData.agent_commission_percent}
                defaultCommissionType={formData.agent_commission_type}
                productId={formData.product_group_name ? formData.product_group_id : formData.native_product_id.toString()}
                insurerId={formData.product_group_name ? formData.insurer.id : ''}
                setSalesTeamIds={setSalesTeamIds}
              />
            </div>
          </>
        )}
        <div className="d-flex justify-content-end gap-2 mt-3">
          <Button onClick={handleSubmit} className="d-flex align-items-center justify-content-center gap-1" width="sm" isLoading={isFormProcessing}>
            <Flexicon icon={'edit-05'} variant="line" size={15} />
            <span className="d-none d-sm-inline">{t('update')}</span>
          </Button>
          {/* <Button text={t('cancel')} color="light" width="sm" onClick={() => setIsEdit(false)} /> */}
        </div>
      </div>
      <EditRevisedCommission
        isOpen={rCommissionEditVisible}
        onCancel={() => {
          setIsRCommissionEditVisible(false);
        }}
        uiFormData={uiFormData}
        setRCommisSionData={setRCommisSionData}
        rCommisSionData={rCommisSionData}
        currentTeamMemberId={editTeamMemberId}
        currentTeamId={currentTeamId}
        onEdit={(data: any) => onRCommissionEdit(data)}
        isFormProcessing={isFormProcessing}
      />
    </div>
  );
}
