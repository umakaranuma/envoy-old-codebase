'use client';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import ServiceProviderList from './ServiceProviderList';
import Received from './received/Received';
import RecommendationDocumentation from './recommandation-document/RecommendationDocumentation';
import { getQuotationBasicInfo } from '../../api-service';
import { initRequestFormData } from '../../model';
import { formatDate } from '@/helpers/services/commonService';
import GoBack from '@/components/others/page-related/GoBack';
import { useBreadcrumb } from '@/contexts/BreadcrumbContext';
import OpportunityTypes from '../risk-types/OpportunityTypes';

function ViewQuotation() {
  const t = useTrans('label.quotations,otr.common');
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setCustomBreadcrumb } = useBreadcrumb();
  const [skeleton, setSkeleton] = useState(true);
  const [rData, setRData] = useState(initRequestFormData);
  const [tab, setTab] = useState('quotations');
  const params = useParams();
  const quotationId = params.quotationId?.toString() || '';
  const [activeSelectedTab, setSelectedActiveTab] = useState(0);
  const [receivedTabKey, setReceivedTabKey] = useState(0);

  useEffect(() => {
    setCustomBreadcrumb({
      text: rData?.code,
      backurl: '/crm/a/quotations',
    });
    return () => setCustomBreadcrumb(null);
  }, [setCustomBreadcrumb, rData]);

  useEffect(() => {
    const tab = searchParams.get('t') || 'quotations';
    toggleTableTab(tab);
  }, [searchParams]);

  const toggleTableTab = (activeTab: string) => {
    setTab(activeTab);
    router.push(`/crm/a/quotations/${quotationId}?t=${activeTab}`, { scroll: false });
  };

  useEffect(() => {
    if (!quotationId) return;

    const fetchData = async () => {
      try {
        setSkeleton(true);

        const basicInfoResponse = await getQuotationBasicInfo(quotationId);
        if (basicInfoResponse?.is_success) {
          setRData(basicInfoResponse.result);
        }

        setSkeleton(false);
      } catch (error) {
        console.error('Error fetching data:', error);
        setSkeleton(false);
      }
    };

    fetchData();
  }, [quotationId]);

  return (
    <>
      <GoBack goTo={() => router.push('/crm/a/quotations')} title={t('quotation_details')} />
      <div className="panel">
        <div className="panel-title">{t('quotation_details')}</div>
        <div className="row">
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('quotation_request_id')} value={rData?.code || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('requested_by')} value={rData?.created_by_name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('requested_date')} value={formatDate(rData?.requested_data) || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('stage')} value={rData?.status || '-'} skeleton={skeleton} />
          </div>
          <div className="col-6 col-md-6 col-lg-4 mb-3">
            <Description label={t('request_type')} value={rData?.request_type || '-'} skeleton={skeleton} />
          </div>
        </div>
      </div>
      {/* <div className="panel">
        <OpportunityTypes quotationData={rData} />
      </div> */}
      {rData.opportunity_type?.length > 0 && (
        <div className="panel">
          <div className="panel-title">{t('risk_details')}</div>
          <div className="il-box-tab">
            {rData.opportunity_type.map((riskType: any, index) => (
              <div key={riskType.id} className={`il-box-tab-item ${activeSelectedTab === index ? 'active' : ''}`} onClick={() => setSelectedActiveTab(index)}>
                {riskType.name}
              </div>
            ))}
          </div>
          {rData.opportunity_type.map((riskType: any, index) =>
            activeSelectedTab === index ? <OpportunityTypes leadId={rData.opportunity_id?.toString()} riskTypeId={riskType.id} customerId={rData.customer_id?.toString()} key={riskType.id} /> : null,
          )}
        </div>
      )}
      <div className="panel">
        <div className="panel-title">{t('request_details')}</div>
        <ServiceProviderList setReceivedTabKey={setReceivedTabKey} />
      </div>
      <div className="panel">
        <div className="il-box-tab">
          <div className={`il-box-tab-item ${tab === 'quotations' ? 'active' : ''}`} onClick={() => toggleTableTab('quotations')}>
            {t('quotations')}
          </div>
          <div className={`il-box-tab-item ${tab === 'recommendation_document' ? 'active' : ''}`} onClick={() => toggleTableTab('recommendation_document')}>
            {t('recommendation_document')}
          </div>
        </div>
        <div>
          {tab === 'quotations' && <Received quotationId={quotationId} customerId={parseInt(rData?.customer_id)} leadId={rData.opportunity_id} key={receivedTabKey} />}
          {tab === 'recommendation_document' && <RecommendationDocumentation quotationId={quotationId} />}
        </div>
      </div>
    </>
  );
}

export default ViewQuotation;
