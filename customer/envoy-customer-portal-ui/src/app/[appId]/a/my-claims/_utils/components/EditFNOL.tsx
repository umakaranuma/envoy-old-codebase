'use client';
import FormTemplateEdit from '@/components/others/common/form/FormTemplateEdit';
import { IElement } from '@/components/others/common/form/template-modal';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import { useParams, useRouter } from 'next/navigation';
import React, { useState } from 'react';
import { updateClaimFNOLInfo } from '../api-service';

function EditFNOL() {
  const tBe = useTrans('be.msg,be.error,be.attri');
  const params = useParams();
  const claimId = params.claimId as string;
  const router = useRouter();
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const appId = params.appId as string;

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
      const responseData = await updateClaimFNOLInfo(claimId, {
        values: formattedFormData,
      });
      setIsFormProcessing(false);

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        router.push(`/${appId}/a/my-claims`);
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <div>
      <FormTemplateEdit
        claimId={claimId}
        onBack={() => router.push(`/${appId}/a/my-claims/${claimId}`)}
        isFormProcessing={isFormProcessing}
        onSubmit={(data: IElement[]) => onSubmit(data)}
        currentPath={''}
      />
    </div>
  );
}

export default EditFNOL;
