'use client';
import React, { useState } from 'react';
import { IElement } from '@/components/others/common/form/template-modal';
import { useTrans } from '@/helpers/services/lang/langService';
import RiskRegisterEditForm from './forms/RiskRegisterEditForm';
import { toaster } from '@/helpers/services/toaster';
import { useParams, useRouter } from 'next/navigation';
import { updateOneRisk } from '../api-service';

function EditRisk() {
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const router = useRouter();
  const params = useParams();
  const riskId = params.riskId as string;

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
      const responseData = await updateOneRisk(riskId, {
        values: formattedFormData,
      });
      setIsFormProcessing(false);

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        router.push(`/policy/a/risk-register`);
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <RiskRegisterEditForm
      riskId={riskId}
      onBack={() => {
        router.push(`/policy/a/risk-register`);
      }}
      isFormProcessing={isFormProcessing}
      onSubmit={(data: IElement[]) => onSubmit(data)}
      currentPath={`/policy/a/risk-register/${riskId}/edit`}
    />
  );
}

export default EditRisk;
