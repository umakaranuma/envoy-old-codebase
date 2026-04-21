'use client';
import { useParams, useRouter } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import { Description } from '@/components/others/Description';
import { Button, Skeleton } from '@apptimus-ui/ui-element';
import { useTrans } from '@/helpers/services/lang/langService';
import { IFormTemplate } from '@/components/others/common/form/template-modal';
import { getOneRisk } from '../api-service';
import GoTo from '@/components/others/page-related/GoTo';
import { useBreadcrumb } from '@/contexts/BreadcrumbContext';
import RiskHistoryList from './RiskHistoryList';
import { Flexicon } from '@apptimus-ui/flexicon';

function ViewTask() {
  const t = useTrans('label.risk_register,otr.common');
  const params = useParams();
  const riskId = params.riskId as string;
  const [skeleton, setSkeleton] = useState(true);
  const [data, setData] = useState({} as IFormTemplate);
  const router = useRouter();
  const { setCustomBreadcrumb } = useBreadcrumb();
  const [tab, setTab] = useState('histories');

  useEffect(() => {
    setCustomBreadcrumb({
      text: data.risk?.code || '',
      backurl: '/policy/a/risk-register',
    });
    return () => setCustomBreadcrumb(null);
  }, [data]);

  useEffect(() => {
    const fetchData = async () => {
      setSkeleton(true);
      const responseData = await getOneRisk(riskId);
      if (responseData?.is_success) {
        setData(responseData.result);
        setSkeleton(false);
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    toggleTableTab('histories');
  }, []);

  const toggleTableTab = (activeTab: string) => {
    setTab(activeTab);
    // router.push(`/crm/a/quotations/${quotationId}?t=${activeTab}`);
  };

  return (
    <>
      {skeleton ? (
        <Skeleton width="100%" height="200px" />
      ) : (
        <div>
          <GoTo goTo={() => router.push('/policy/a/risk-register')} title={t('risk')} />
          {data?.panels?.length > 0 &&
            data.panels.map((panel, index) => (
              <div className="panel" key={panel.id}>
                <div className="panel-title">{panel.title ? panel.title : ''}</div>
                <div className="row">
                  {index < 1 && (
                    <div className="col-12 col-md-3 mb-3">
                      <Description label={t('latest_policy')} value={data.risk?.latest_policy || '-'} skeleton={skeleton} />
                    </div>
                  )}
                  {data.elements.length > 0 &&
                    data.elements
                      .filter((element) => element.panel_id === panel.id)
                      .map((element) => (
                        <div className={`${element.code !== 'LONG_ANSWER' ? 'col-12 col-md-3' : 'col-12 '} mb-3`} key={element.id}>
                          <Description label={element.label ? element.label : '-'} value={element.value || '-'} isTruncate={element.code !== 'LONG_ANSWER'} skeleton={skeleton} />
                        </div>
                      ))}
                </div>
              </div>
            ))}
          <div className="panel">
            <div className="tap-btn-container my-2">
              <div className="il-tab ms-2">
                <div className={`il-tab-item ${tab === 'histories' ? 'active' : ''}`} onClick={() => toggleTableTab('histories')}>
                  {t('history')}
                </div>
                {/* <div className={`il-tab-item ${tab === 'shortlisted' ? 'active' : ''}`} onClick={() => toggleTableTab('shortlisted')}>
                {t('shortlisted')}
              </div> */}
              </div>
            </div>
            {data.elements.length > 0 && <RiskHistoryList riskId={riskId} tableElements={data.elements} />}
          </div>
          <div className="d-flex justify-content-end">
            <Button onClick={() => router.push(`/policy/a/risk-register/${riskId}/edit`)}>
              <span className="d-flex gap-2">
                <Flexicon icon="pencil-line" variant="line" size={17} />
                <span>{t('edit')}</span>
              </span>
            </Button>
          </div>
        </div>
      )}
    </>
  );
}

export default ViewTask;
