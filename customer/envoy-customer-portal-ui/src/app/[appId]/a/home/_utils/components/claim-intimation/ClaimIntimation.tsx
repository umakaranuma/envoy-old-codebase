'use client';
import { useEffect, useState } from 'react';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { IElement } from '../../../../../../../components/others/common/form/template-modal';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import FormTemplateCreate from '@/components/others/common/form/FormTemplateCreate';
import PolicyInfo from './PolicyInfo';
import { CreateClaim } from '../../api-service';
import { initFormData } from '../../model';

export const ClaimIntimation = ({ policyId, riskInfoIds }: { policyId: string; riskInfoIds: string }) => {
  const tBe = useTrans('be.msg,be.error,be.attri');
  const params = useParams();
  const appId = params.appId as string;

  const router = useRouter();
  const searchParams = useSearchParams();
  const [tab, setTab] = useState('policy_info');
  const [formData, setFormData] = useState(initFormData);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const formId = searchParams.get('tid') || '';

  useEffect(() => {
    const tab = searchParams.get('t') || 'policy_info';
    onFormChange('form_id', formId);
    toggleTableTab(tab);
    if (policyId) {
      onFormChange('policy_id', policyId);
    }
    if (riskInfoIds) {
      onFormChange('risk_info_ids', riskInfoIds.split(','));
    }
  }, [policyId]);

  const toggleTableTab = (activeTab: string) => {
    setTab(activeTab);
    router.push(`/${appId}/a/home/claim-intimation?t=${activeTab}&pid=${policyId}`);
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
      const responseData = await CreateClaim({
        form_id: formData.form_id,
        policy_id: policyId,
        is_myself: formData.is_myself,
        values: formattedFormData,
        risk_info_ids: formData.risk_info_ids,
      });

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        router.push(`/${appId}/a/my-claims`);
        setIsFormProcessing(false);
      }
    } catch (error) {
      console.error('An error occurred:', error);
    } finally {
      setIsFormProcessing(false);
    }
  }

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  };

  const handleNextForm = () => {
    if (formData.form_id) {
      toggleTableTab('form');
    } else {
      toaster.error(tBe('claim_form_not_found'));
    }
  };
  return (
    <>
      {tab === 'policy_info' && (
        <PolicyInfo
          setIsFormTemplateVisible={handleNextForm}
          templateId={(id: any) => {
            onFormChange('form_id', id);
          }}
          onBack={() => router.push(`/${appId}/a/home`)}
          // currentPath={`/${appId}/a/home/create?t=policy_info&pid=${policyId}`}
        />
      )}
      {tab === 'form' && (
        <FormTemplateCreate
          currentPath={`/${appId}/a/home/claim-intimation?t=${tab}&pid=${policyId}&tid=${formData.form_id}`}
          templateId={formData.form_id}
          onBack={() => {
            toggleTableTab('policy_info');
          }}
          isFormProcessing={isFormProcessing}
          onSubmit={(data: IElement[]) => onSubmit(data)}
        />
      )}
    </>
  );
};
