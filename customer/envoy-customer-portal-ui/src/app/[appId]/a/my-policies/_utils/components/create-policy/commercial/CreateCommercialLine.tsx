'use client';
import FormStepper from '@/components/others/common/form/FormStepper';
import GoTo from '@/components/others/page-related/GoTo';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import { Step } from '@/components/others/common/form/template-modal';
import RiskInformation from './RiskInformation';
import PolicyHolderInfo from '../individual/forms/PolicyHolderInfo';
import CoverageInfo from '../individual/forms/CoverageInfo';
import PaymentInfo from '../individual/forms/PaymentInfo';
import SupportingDocuments from '../individual/forms/SupportingDocuments';
import TermsAndCondition from '../individual/forms/TermsAndCondition';
import ReviewAndSubmit from '../individual/forms/ReviewAndSubmit';

function CreateCommercialLine({ productId, riskTypeId, requestId }: { productId: string; riskTypeId: string; requestId: string }) {
  const t = useTrans('label.my_policy,otr.common');
  const router = useRouter();
  const params = useParams();
  const appId = params.appId as string;
  const [activeTab, setActiveTab] = useState('personal_info');
  const searchParams = useSearchParams();
  // const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [currentTab, setCurrentTab] = useState<Step>();
  const steps = [
    { title: 'Personal Info', id: 1 },
    { title: 'Risk Info', id: 2 },
    { title: 'Coverage Info', id: 3 },
    { title: 'Payment Info', id: 4 },
    { title: 'Supporting Documents', id: 5 },
    { title: 'Terms and Conditions', id: 6 },
    { title: 'Review and Submit', id: 7 },
  ];

  useEffect(() => {
    const tab = searchParams.get('t') || 'personal_info';
    toggleTableTab(tab);
  }, []);

  const toggleTableTab = (activeTab: string) => {
    setActiveTab(activeTab);
    setCurrentTab(steps.find((step) => step.title.toLowerCase().replace(/\s+/g, '_') === activeTab) || steps[0]);
    router.push(`/${appId}/a/my-policies/create-commercial?t=${activeTab}&pId=${productId}&rId=${riskTypeId}&reqId=${requestId}`, { scroll: false });
  };

  return (
    <>
      <div className="d-flex align-items-center gap-2 mb-2">
        <GoTo goTo={() => router.push(`/${appId}/a/my-policies`)} />
        <div className="fs-15 fw-medium">{t('buy_new_policy')}</div>
      </div>
      <div className="text-muted fs-14">Ready to secure coverage? Provide the necessary details below to request your new insurance policy, and we’ll guide you through the next steps.</div>
      <div className="my-3">
        <FormStepper steps={steps} currentTabId={currentTab ? currentTab.id : steps[0].id} />
      </div>
      <div className="panel">
        {activeTab === 'personal_info' && (
          <PolicyHolderInfo setToggleTab={() => toggleTableTab('risk_info')} requestId={requestId} onBack={() => router.push(`/${appId}/a/my-policies`)} type="policy" />
        )}
        {activeTab === 'coverage_info' && (
          <CoverageInfo
            setToggleTab={(tab: string) => {
              if (tab === 'personal_info') {
                toggleTableTab('risk_info');
              } else {
                toggleTableTab(tab);
              }
            }}
            requestId={requestId}
            type="policy"
          />
        )}
        {activeTab === 'payment_info' && <PaymentInfo setToggleTab={(tab: string) => toggleTableTab(tab)} requestId={requestId} type="policy" />}
        {activeTab === 'supporting_documents' && <SupportingDocuments setToggleTab={(tab: string) => toggleTableTab(tab)} requestId={requestId ? requestId : ''} type="policy" />}
        {activeTab === 'terms_and_conditions' && <TermsAndCondition setToggleTab={(tab: string) => toggleTableTab(tab)} requestId={requestId ? requestId : ''} />}
        {activeTab === 'risk_info' && (
          <RiskInformation
            setToggleTab={(tab: string) => {
              toggleTableTab(tab);
            }}
            requestId={requestId ? requestId : ''}
            type="policy"
          />
        )}
        {activeTab === 'review_and_submit' && <ReviewAndSubmit setToggleTab={(tab: string) => toggleTableTab(tab)} requestId={requestId ? requestId : ''} type={'policy'} />}
      </div>
    </>
  );
}

export default CreateCommercialLine;
