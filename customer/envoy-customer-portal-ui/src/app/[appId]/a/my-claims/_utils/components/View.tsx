'use client';
import GoTo from '@/components/others/page-related/GoTo';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import EvaluationInfo from './EvaluationInfo';
import FNOL from './FNOL';

function View() {
  const t = useTrans('label.claim,label.my_claims,otr.common');
  const params = useParams();
  const router = useRouter();
  const appId = params.appId as string;
  const claimId = params.claimId as string;
  const [activeTab, setActiveTab] = useState('fnol');
  const searchParams = useSearchParams();

  useEffect(() => {
    const tab = searchParams.get('t') || 'fnol';
    toggleTableTab(tab);
  }, []);

  const toggleTableTab = (activeTab: string) => {
    setActiveTab(activeTab);
    router.push(`/${appId}/a/my-claims/${claimId}?t=${activeTab}`, { scroll: false });
  };

  return (
    <>
      <div className="d-flex align-items-center gap-2 mb-4">
        <GoTo goTo={() => router.push(`/${appId}/a/my-claims`)} />
        <div className="fs-15 fw-medium">{t('my_claims')}</div>
      </div>
      <div className="mt-3 px-3 bg-light py-2 mb-3 rounded-1">
        <div className="il-tab pb-2 overflow-x-auto text-nowrap" style={{ scrollbarWidth: 'none' }}>
          <div className={`il-tab-item ${activeTab === 'fnol' ? 'active' : ''}`} onClick={() => toggleTableTab('fnol')}>
            {t('first_notice_of_loss_forms')}
          </div>
          <div className={`il-tab-item ${activeTab === 'evaluation' ? 'active' : ''}`} onClick={() => toggleTableTab('evaluation')}>
            {t('evaluation_info')}
          </div>
        </div>
      </div>
      <div>
        {activeTab === 'fnol' && <FNOL />}
        {activeTab === 'evaluation' && <EvaluationInfo />}
      </div>
    </>
  );
}

export default View;
