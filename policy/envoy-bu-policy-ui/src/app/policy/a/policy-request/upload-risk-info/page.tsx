'use client';
import React, { useEffect, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { useSearchParams } from 'next/navigation';
import Upload from '../_utils/components/create/upload-risk-info/Upload';
import { submitExcelData, uploadExcelToJson } from '../_utils/api-service';
import { getAllOpportunityTypeFormAttributes } from '@/components/others/common/lead/api-service';
import { getAllOpportunityTypeFormElements } from '@/components/others/common/risk-type-view/api-service';

export default function Page() {
  const t = useTrans('label.policy_request,otr.common');
  const searchParams = useSearchParams();
  const formId = searchParams.get('leadId')?.toString() || '';
  const opportunityId = searchParams.get('leadId')?.toString() || '';
  const [configId, setConfigId] = useState('');
  const [formAttributes, setFormAttributes] = useState<any[]>([]);
  const [_, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchTypeConfig = async () => {
      if (!formId) return;
      try {
        setIsLoading(true);
        setFormAttributes([]);
        const configResponse = await getAllOpportunityTypeFormAttributes(formId, 'ONBOARDING');
        const FormId = configResponse?.is_success ? configResponse.result.form_id : '';
        const config_id = configResponse?.is_success ? configResponse.result.config_id : '';
        setConfigId(config_id);
        const attributesResponse = await getAllOpportunityTypeFormElements(FormId);
        if (attributesResponse?.is_success) {
          const simplifiedArray = attributesResponse.result.map((item: any) => ({
            ...item,
            isRequired: item.is_required === 1,
          }));
          setFormAttributes(simplifiedArray || []);
        }
      } catch (error) {
        console.error('Error fetching type config:', error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchTypeConfig();
  }, [formId]);

  const handleFileUpload = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await uploadExcelToJson(formData);
      return response;
    } catch (error) {
      console.error('Error uploading file:', error);
      throw error;
    }
  };

  const handleMappingSubmit = async (mappingData: any) => {
    try {
      const response = await submitExcelData(opportunityId, configId, mappingData);
      if (response.is_success) {
        return response;
      } else {
        throw new Error(response.message || 'Failed to submit mapping');
      }
    } catch (error) {
      console.error('Error submitting mapping:', error);
      throw error;
    }
  };

  return (
    <div>
      <Upload
        backUrl={`/policy/a/policy-request/create`}
        title={t('risk_info_upload')}
        mappingFields={formAttributes}
        onFileUpload={handleFileUpload}
        onMappingSubmit={(mappingData: any) => handleMappingSubmit(mappingData)}
      />
    </div>
  );
}
