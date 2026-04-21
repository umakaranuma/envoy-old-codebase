'use client';
import FormStepper from '@/components/others/common/form/FormStepper';
import GoTo from '@/components/others/page-related/GoTo';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import { IClaimTemplate, IElement, Step } from '@/components/others/common/form/template-modal';
import { getFormsOfCustomer } from '@/components/others/common/form/api-service';
import { Skeleton } from '@apptimus-ui/ui-element';
import { createPolicyFormTemplate } from '../../../my-policies/_utils/api-service';
import PolicyHolderInfo from '../../../my-policies/_utils/components/create-policy/individual/forms/PolicyHolderInfo';
import CoverageInfo from '../../../my-policies/_utils/components/create-policy/individual/forms/CoverageInfo';
import PaymentInfo from '../../../my-policies/_utils/components/create-policy/individual/forms/PaymentInfo';
import SupportingDocuments from '../../../my-policies/_utils/components/create-policy/individual/forms/SupportingDocuments';
import TermsAndCondition from '../../../my-policies/_utils/components/create-policy/individual/forms/TermsAndCondition';
import CreatePolicyFormTemplate from '../../../my-policies/_utils/components/create-policy/individual/forms/CreatePolicyFormTemplate';
import ReviewAndSubmit from '../../../my-policies/_utils/components/create-policy/individual/forms/ReviewAndSubmit';

function Create({ formId, productId, riskTypeId }: { formId: string; productId: string; riskTypeId: string }) {
  const t = useTrans('label.my_policy,otr.common');
  const router = useRouter();
  const params = useParams();
  const appId = params.appId as string;
  const [activeTab, setActiveTab] = useState('risk_info');
  const searchParams = useSearchParams();
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const preSteps = ['Personal Info', 'Coverage Info', 'Payment Info', 'Supporting Documents', 'Terms and Conditions', 'Review and Submit'];
  const [currentTabIndex, setCurrentTabIndex] = useState(0);
  const [currentTab, setCurrentTab] = useState<Step>();
  const [templateData, setTemplateData] = useState<IClaimTemplate>();
  const [breakTabId, setBreakTabId] = useState<number | null>(null);
  const [requestId, setRequestId] = useState<string | null>(null);

  useEffect(() => {
    const tab = searchParams.get('t') || 'risk_info';
    toggleTableTab(tab);
    fetchTemplateData();
  }, []);

  useEffect(() => {
    if (currentTab?.title && preSteps.includes(currentTab.title)) {
      toggleTableTab(currentTab.title.toLowerCase().replace(/\s+/g, '_'));
    }
  }, [currentTab]);

  const toggleTableTab = (activeTab: string) => {
    setActiveTab(activeTab);
    router.push(`/${appId}/a/my-quotations/create?t=${activeTab}&fId=${formId}&pId=${productId}&rId=${riskTypeId}&reqId=${requestId}`, { scroll: false });
  };

  const handleToggleStaticForm = (tab: string) => {
    templateData && templateData.steps && templateData.steps.length > 0 && setCurrentTab(templateData.steps.find((step: Step) => step.title.toLowerCase().replace(/\s+/g, '_') === tab));
    const index = templateData?.steps.findIndex((step: Step) => step.title.toLowerCase().replace(/\s+/g, '_') === tab) || 0;
    setCurrentTabIndex(index < 0 ? 0 : index);
    toggleTableTab(tab);
  };

  const fetchTemplateData = async () => {
    if (formId) {
      const responseData = await getFormsOfCustomer(formId);
      if (responseData?.is_success) {
        let steps: any[] = [];
        if (responseData.result.steps && responseData.result.steps.length > 0) {
          const maxId = Math.max(...responseData.result.steps.map((step: any) => step.id));
          console.log('maxId', maxId);
          setBreakTabId(maxId);
          const newSteps = preSteps.map((title, index) => ({
            id: maxId + index + 1,
            title,
          }));
          responseData.result.steps = [...responseData.result.steps, ...newSteps];
        } else {
          steps = [{ title: 'Risk Information', id: 1 }];
          const maxId = Math.max(...steps.map((step: any) => step.id));
          const newSteps = preSteps.map((title, index) => ({
            id: maxId + index + 1,
            title,
          }));
          responseData.result.steps = [...steps, ...newSteps];
        }

        // const defaultTabSlug = responseData.result.steps[0].title.toLowerCase().replace(/\s+/g, '_');
        // const foundIndex = responseData.result.steps.findIndex((step: Step) => step.title.toLowerCase().replace(/\s+/g, '_') === defaultTabSlug);

        // if (foundIndex !== -1) {
        //     const step = responseData.result.steps[foundIndex];
        //     setCurrentTab(step);
        //     setCurrentTabIndex(foundIndex);
        // }
        setTemplateData(responseData.result);
        const tabSlug = searchParams.get('t') || 'risk_info';
        const foundIndex = responseData.result.steps.findIndex((step: Step) => step.title.toLowerCase().replace(/\s+/g, '_') === tabSlug);
        console.log('foundIndex', foundIndex);
        console.log('tabSlug', tabSlug);

        if (foundIndex !== -1) {
          setCurrentTab(responseData.result.steps[foundIndex]);
          setCurrentTabIndex(foundIndex);
        } else {
          setCurrentTab(responseData.result.steps[0]);
          setCurrentTabIndex(0);
        }
      }
    }
  };

  async function onSubmit(data: IElement[]) {
    setIsFormProcessing(true);
    const formattedFormData = data.reduce(
      (acc, curr) => {
        acc[curr.id.toString()] = curr.value;
        return acc;
      },
      {} as Record<string, any>,
    );

    try {
      const responseData = await createPolicyFormTemplate({
        form_id: formId,
        type: 'quotation',
        risk_type_id: riskTypeId,
        vendor_product_id: productId,
        values: formattedFormData,
      });
      setIsFormProcessing(false);

      if (responseData.is_success) {
        const requestId = responseData.result.request_id;
        setRequestId(requestId);
        const nextIndex = currentTabIndex + 1;
        const nextStep = templateData?.steps[nextIndex];
        setCurrentTab(nextStep);
        setCurrentTabIndex(nextIndex);
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <>
      <div className="d-flex align-items-center gap-2 mb-2">
        <GoTo goTo={() => router.push(`/${appId}/a/my-quotations`)} />
        <div className="fs-15 fw-medium">{t('request_new_quotation')}</div>
      </div>
      {/* <div className='text-muted fs-14'>Ready to secure coverage? Provide the necessary details below to request your new insurance policy, and we’ll guide you through the next steps.</div> */}
      <div className="my-3">
        {templateData && templateData.steps.length > 0 ? (
          <FormStepper steps={templateData.steps} currentTabId={currentTab ? currentTab.id : templateData.steps[0].id} />
        ) : (
          <Skeleton height="100px" width="100%" />
        )}
      </div>
      {templateData ? (
        <div className="panel">
          {activeTab === 'personal_info' && (
            <PolicyHolderInfo setToggleTab={(tab: string) => handleToggleStaticForm(tab)} requestId={requestId} onBack={() => handleToggleStaticForm('risk_info')} type="quotation" />
          )}
          {activeTab === 'coverage_info' && <CoverageInfo setToggleTab={(tab: string) => handleToggleStaticForm(tab)} requestId={requestId} type="quotation" />}
          {activeTab === 'payment_info' && <PaymentInfo setToggleTab={(tab: string) => handleToggleStaticForm(tab)} requestId={requestId} type="quotation" />}
          {activeTab === 'supporting_documents' && <SupportingDocuments setToggleTab={(tab: string) => handleToggleStaticForm(tab)} requestId={requestId ? requestId : ''} type="quotation" />}
          {activeTab === 'terms_and_conditions' && <TermsAndCondition setToggleTab={(tab: string) => handleToggleStaticForm(tab)} requestId={requestId ? requestId : ''} />}
          {activeTab === 'risk_info' && (
            <CreatePolicyFormTemplate
              currentTabIndex={currentTabIndex}
              setCurrentTabIndex={setCurrentTabIndex}
              onBack={() => router.push(`/${appId}/a/my-quotations`)}
              isFormProcessing={isFormProcessing}
              onSubmit={(data: IElement[]) => onSubmit(data)}
              templateData={templateData}
              setCurrentTab={setCurrentTab}
              breakTabId={breakTabId}
              currentTab={currentTab ? currentTab : templateData.steps[0]}
            />
          )}
          {activeTab === 'review_and_submit' && <ReviewAndSubmit setToggleTab={(tab: string) => handleToggleStaticForm(tab)} requestId={requestId ? requestId : ''} type="quotation" />}
        </div>
      ) : (
        <Skeleton height="200px" width="100%" />
      )}
    </>
  );
}

export default Create;
