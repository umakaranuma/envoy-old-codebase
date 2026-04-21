'use client';
import FormTemplateEdit from '@/components/others/common/form/FormTemplateEdit';
import { IElement } from '@/components/others/common/form/template-modal';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import React, { useState } from 'react';
import { updateEvaluation } from '../../api-service';

function EditClaim() {
  const tBe = useTrans('be.msg,be.error,be.attri');
  const params = useParams();
  const templateId = params.evaluationTemplateId as string;
  const claimId = params.claimId as string;
  const policyId = useSearchParams().get('pid') || '';
  const router = useRouter();
  const [isFormProcessing, setIsFormProcessing] = useState(false);

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
      const responseData = await updateEvaluation(claimId, {
        values: formattedFormData,
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

  return (
    <div>
      <FormTemplateEdit
        claimId={claimId}
        onBack={() => router.push(`/policy/a/claim/${claimId}?t=policy_info&pid=${policyId}&tid=${templateId}`)}
        isFormProcessing={isFormProcessing}
        onSubmit={(data: IElement[]) => onSubmit(data)}
        currentPath={''}
      />
    </div>
  );
}

export default EditClaim;
