'use client';
import React, { useEffect, useState } from 'react';
import RiskRegisterCreateForm from './forms/RiskRegisterCreateForm';
import { useRouter } from 'next/navigation';
import { IElement } from '@/components/others/common/form/template-modal';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { CreateRisk } from '../api-service';

function CreateRiskRegister({ customerId, leadId, riskId }: { customerId: string; leadId: string; riskId: string }) {
  const tBe = useTrans('be.msg,be.error,be.attri');
  const router = useRouter();
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({ customer_id: '', risk_type_id: '', lead_id: '' });

  useEffect(() => {
    router.push(`/policy/a/risk-register/create?cId=${formData.customer_id || customerId}&lId=${formData.lead_id || leadId}&rId=${formData.risk_type_id || riskId}`);
    setFormData({ customer_id: customerId, risk_type_id: riskId, lead_id: leadId });
  }, []);

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
      const responseData = await CreateRisk({
        ...formData,
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
    <RiskRegisterCreateForm
      riskId={riskId}
      onBack={() => router.push(`/policy/a/risk-register`)}
      isFormProcessing={isFormProcessing}
      onSubmit={(data: IElement[]) => onSubmit(data)}
      riskTypeId={formData.risk_type_id || riskId}
      currentPath={`/policy/a/risk-register/create?cId=${formData.customer_id || customerId}&lId=${formData.lead_id || leadId}&rId=${formData.risk_type_id || riskId}`}
    />
  );
}

export default CreateRiskRegister;
