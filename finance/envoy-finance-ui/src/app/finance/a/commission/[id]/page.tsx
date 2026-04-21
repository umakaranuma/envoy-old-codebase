'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { getOneAgentCommissionSettlements } from '../_utils/api-service';
import { Description } from '@/components/others/Description';
import { IBrokerageCommissionResult } from '../_utils/model';
import SingleAgentCommisonList from './SingleAgentCommisonList';
import GoBack from '@/components/others/page-related/GoBack';
import { Label } from '@apptimus-ui/ui-element';
import ProfileInfo from '@/components/others/page-related/ProfileInfo';
import { useBreadcrumb } from '@/contexts/BreadcrumbContext';
import { hexToRgba, thousandSeparator } from '@/helpers/services/commonService';

function page() {
  const t = useTrans('label.commission,otr.common');
  const params = useParams();
  const viewId = params.id?.toString() || '';
  const router = useRouter();
  const { setCustomBreadcrumb } = useBreadcrumb();
  const [formData, setFormData] = useState<IBrokerageCommissionResult>({} as IBrokerageCommissionResult);
  const [skeleton, setSkeleton] = useState(true);

  useEffect(() => {
    setCustomBreadcrumb({
      text: t('view'),
      backurl: '/finance/a/commission?tab=agent_commission',
    });
    return () => setCustomBreadcrumb(null);
  }, [setCustomBreadcrumb]);

  useEffect(() => {
    const fetchData = async () => {
      setSkeleton(true);
      try {
        const responseData = await getOneAgentCommissionSettlements(viewId, true);
        setSkeleton(false);
        if (responseData?.is_success) {
          const data: IBrokerageCommissionResult = responseData.result;
          setFormData(data);
        }
      } catch (error) {
        console.error(error);
      }
    };

    if (viewId) {
      fetchData();
    }
  }, [viewId]);

  return (
    <>
      <GoBack goTo={() => router.back()} title={t('agent_commission')} />
      <div className="panel ">
        <div className="row">
          <div className="col-12 col-md-4 mb-3">
            <Label htmlFor="name" label={t('agent_details')} />
            <ProfileInfo title={formData?.agent_name} subtitle={formData?.agent_email as string} imageKey={formData?.agent_picture} loading={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('dr_cr_note_number')} value={formData?.invoice_number || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('dr_cr_note_amount')} value={thousandSeparator(formData?.invoice_amount ?? 0) || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('total_agent_commission')} value={thousandSeparator(formData?.total_agent_commission ?? 0) || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('revenue_realized_amount')} value={thousandSeparator(formData?.revenue_realized ?? 0) || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('revised_amount')} value={thousandSeparator(formData?.revised_amount ?? 0) || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('deductible')} value={thousandSeparator(formData?.commission_deductible ?? 0) || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('paid_amount')} value={thousandSeparator(formData?.paid_amount ?? 0) || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('outstanding_amount')} value={thousandSeparator(formData?.outstanding ?? 0) || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('credit_period_days')} value={formData?.credit_period_days || '0'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description
              label={t('status')}
              value={
                <div
                  className="rounded-5 fw-semibold badge"
                  style={{ background: hexToRgba(formData?.status_color || '', 0.1), border: `1px solid ${formData?.status_color}`, color: formData?.status_color }}
                >
                  {formData?.status}
                </div>
              }
              skeleton={skeleton}
            />
          </div>
        </div>
      </div>
      <SingleAgentCommisonList commisonId={viewId} />
    </>
  );
}

export default page;
