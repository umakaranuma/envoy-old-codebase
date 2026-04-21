'use client';
import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import PolicyInfo from './PolicyInfo';
import { CreateClaim } from '../../api-service';
import { IElement, IFormTemplate } from '../../../../../../../components/others/common/form/template-modal';
import { initFormData } from '../../model';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import FormCreate from '@/components/others/common/form/FormCreate';
import { getAllOpportunityTypeFormAttributes } from '@/components/others/common/lead/api-service';
import { getFormsElements } from '@/components/others/common/form/api-service';
import Link from 'next/link';
import GoTo from '@/components/others/page-related/GoTo';

export const ClaimCreate = ({ policyId, riskId, infoId }: { policyId: string; riskId: string; infoId: string }) => {
  const tBe = useTrans('be.msg,be.error,be.attri');
  const t = useTrans('otr.common,be.msg');
  const router = useRouter();
  const searchParams = useSearchParams();
  const [tab, setTab] = useState('policy_info');
  const [formData, setFormData] = useState(initFormData);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [templateData, setTemplateData] = useState<IFormTemplate>({} as IFormTemplate);
  const backURL = encodeURIComponent(window.location.pathname + window.location.search);

  useEffect(() => {
    const tab = searchParams.get('t') || 'policyholder_info';
    toggleTableTab(tab);
    if (policyId) {
      onFormChange('policy_id', policyId);
    }
    if (infoId) {
      onFormChange('risk_info_ids', infoId.split(','));
    }
  }, [searchParams]);

  // const toggleTableTab = (activeTab: string) => {
  //   setTab(activeTab);
  //   const pid = formData.policy_id || searchParams.get('pid') || '';
  //   if (activeTab === 'form') {
  //     router.push(`/policy/a/claim/create?t=${activeTab}&pid=${pid}&tid=${templateId}`);
  //   } else if (activeTab === 'policy_info') {
  //     router.push(`/policy/a/claim/create?t=${activeTab}&pid=${pid}`);
  //   }
  // };

  const toggleTableTab = (activeTab: string) => {
    setTab(activeTab);
    router.push(`/policy/a/claim/create?t=${activeTab}&pid=${policyId}&rid=${riskId}&infoId=${infoId}`);
  };

  async function onSubmit(data: IElement[]) {
    setIsFormProcessing(true);
    try {
      const responseData = await CreateClaim({
        form_id: formData.form_id,
        policy_id: formData.policy_id,
        risk_info_ids: formData.risk_info_ids,
        is_myself: formData.is_myself,
        values: data,
      });
      setIsFormProcessing(false);

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        router.push(`/policy/a/claim`);
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const responseData = await getAllOpportunityTypeFormAttributes(riskId, 'CLAIM');
        if (responseData?.is_success && responseData.result.form_id) {
          onFormChange('form_id', responseData.result.form_id);
          const response = await getFormsElements(responseData.result.form_id.toString());
          if (response?.is_success) {
            setTemplateData(response.result);
          }
          //setLoading(false);
        }
      } catch (error) {
        console.error('Error fetching form attributes:', error);
      }
    };

    if (riskId) {
      fetchData();
    }
  }, [riskId]);

  return (
    <>
      {tab === 'policy_info' && policyId && <PolicyInfo setIsFormTemplateVisible={() => toggleTableTab('form')} onBack={() => router.push(`/policy/a/claim`)} policyId={policyId} />}
      {tab === 'form' && (
        // <FormTemplateCreate
        //   currentPath={`/policy/a/claim/create?t=${tab}&pid=${policyId}&tid=${templateId}`}
        //   templateId={templateId}
        //   onBack={() => {
        //     toggleTableTab('policy_info');
        //   }}
        //   isFormProcessing={isFormProcessing}
        //   onSubmit={(data: IElement[]) => onSubmit(data)}
        // />
        <>
          {formData.form_id === '' ? (
            <div className="text-center p-5 panel">
              <GoTo goTo={() => toggleTableTab('policy_info')} title={t('back')} />
              <div className="text-muted fs-15 fw-semibold my-2">{t('no_form_config')}</div>
              <Link className="text-primary clickable-text fs-14" href={`/a/product-categories/${riskId}?t=forms&backUrl=${backURL}`}>
                {t('configure_it_now')}
              </Link>
            </div>
          ) : (
            <FormCreate onBack={() => toggleTableTab('policy_info')} isFormProcessing={isFormProcessing} onSubmit={(data: IElement[]) => onSubmit(data)} templateData={templateData} />
          )}
        </>
      )}
    </>
  );
};
