'use client';
import { useEffect, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import GoTo from '@/components/others/page-related/GoTo';
import PolicyInfo from './claim-create/PolicyInfo';
import FormTemplateView from '@/components/others/common/form/FormTemplateView';
import { Button } from '@apptimus-ui/ui-element';
import { toaster } from '@/helpers/services/toaster';
import { getOneClaim, sendIntimationEmail } from '../api-service';
import FormTemplateEvaluationView from './evalution/FormTemplateEvaluationView';
import { useBreadcrumb } from '@/contexts/BreadcrumbContext';
import { Flexicon } from '@apptimus-ui/flexicon';

export const ClaimView = () => {
  const t = useTrans('label.claim,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const params = useParams();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setCustomBreadcrumb } = useBreadcrumb();
  const [tab, setTab] = useState('policy_info');
  const [templateId, setTemplateId] = useState<string>('');
  const [currentPolicyId, setCurrentPolicyId] = useState('');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const claimId = params.claimId?.toString() || '';
  const policyId = searchParams.get('pid') || '';
  const formId = searchParams.get('tid') || '';
  const [isIntimationVisible, setIsIntimationVisible] = useState(false);

  useEffect(() => {
    const tab = searchParams.get('t') || 'policy_info';
    setTemplateId(formId);
    setCurrentPolicyId(policyId);
    toggleTableTab(tab);
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneClaim(claimId);
      responseData?.is_success && setIsIntimationVisible(responseData.result.claim_status_type === 'claim_draft' ? true : false);
    };

    if (claimId) {
      fetchData();
    }
  }, [claimId]);

  useEffect(() => {
    setCustomBreadcrumb({
      text: `CLM-${String(claimId).padStart(5, '0')}`,
      backurl: '/policy/a/claim',
    });
    return () => setCustomBreadcrumb(null);
  }, []);

  const toggleTableTab = (activeTab: string) => {
    setTab(activeTab);
    if (activeTab === 'policy_info') {
      router.push(`/policy/a/claim/${claimId}?t=${activeTab}&pid=${policyId}&tid=${formId}`);
    } else {
      router.push(`/policy/a/claim/${claimId}?t=${activeTab}&tid=${formId}`);
    }
  };

  const navigateToEvaluation = () => {
    router.push(`/policy/a/claim/${claimId}/evaluation/${formId}?pid=${currentPolicyId}`);
  };

  useEffect(() => {
    console.log('templateId', templateId);
  }, [templateId]);

  async function handleSendIntimationNotice() {
    setIsFormProcessing(true);

    try {
      const responseData = await sendIntimationEmail({
        claim_ids: [claimId],
      });
      setIsFormProcessing(false);

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <>
      <GoTo goTo={() => router.push('/policy/a/claim')} title={t('first_notice_of_loss_forms')} />
      <div className="d-flex justify-content-end gap-3 my-3">
        <Button color="light" onClick={navigateToEvaluation} className="text-primary" text={t('start_evaluation')} />
        {isIntimationVisible && (
          <Button color="primary" className="d-flex align-items-center gap-1" onClick={handleSendIntimationNotice} isLoading={isFormProcessing}>
            <span className="d-none d-sm-inline">{t('send_intimation_notice')}</span>
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M7.74976 10.25L16.4998 1.50002M7.85608 10.5234L10.0462 16.1551C10.2391 16.6512 10.3356 16.8993 10.4746 16.9717C10.5951 17.0345 10.7386 17.0345 10.8592 16.9719C10.9983 16.8997 11.095 16.6517 11.2886 16.1558L16.7805 2.08269C16.9552 1.63504 17.0426 1.41121 16.9948 1.26819C16.9533 1.14398 16.8558 1.04651 16.7316 1.00501C16.5886 0.957234 16.3647 1.04458 15.9171 1.21927L1.84398 6.71122C1.34808 6.90474 1.10013 7.0015 1.02788 7.14059C0.965237 7.26116 0.965322 7.4047 1.0281 7.5252C1.10052 7.66421 1.34859 7.76067 1.84471 7.95361L7.47638 10.1437C7.57708 10.1829 7.62744 10.2024 7.66984 10.2327C7.70742 10.2595 7.74028 10.2924 7.76709 10.3299C7.79734 10.3723 7.81692 10.4227 7.85608 10.5234Z"
                stroke="white"
                strokeWidth="1.66667"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </Button>
        )}
        <Button onClick={() => router.push(`/policy/a/claim/${claimId}/edit`)}>
          <span className="d-flex gap-2">
            <Flexicon icon="pencil-line" variant="line" size={17} />
            <span>{t('edit')}</span>
          </span>
        </Button>
      </div>
      {tab === 'policy_info' && (
        <PolicyInfo
          setIsFormTemplateVisible={() => toggleTableTab('form')}
          onBack={() => {
            router.push(`/policy/a/claim`);
          }}
          policyId={currentPolicyId}
        />
      )}
      {tab === 'form' && (
        <FormTemplateView
          claimId={claimId}
          onBack={() => toggleTableTab('policy_info')}
          currentPath={`/policy/a/claim/${claimId}?t=form&tid=${formId}`}
          handleNextPage={() => toggleTableTab('evaluation_form')}
        />
      )}
      {tab === 'evaluation_form' && <FormTemplateEvaluationView claimId={claimId} onBack={() => toggleTableTab('form')} currentPath={`/policy/a/claim/${claimId}?t=evaluation_form&tid=${formId}`} />}
    </>
  );
};
