'use client';
import React, { useEffect, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import Upload from '../../../_utils/components/tabs/opportunity-type/_utils/compoents/upload/Upload';
import { useParams } from 'next/navigation';
import { getAllOpportunityTypeConfig, getAllOpportunityTypeFormAttributes } from '../../../_utils/api-service';
import { submitExcelData, uploadExcelToJson } from '../../../_utils/components/tabs/opportunity-type/_utils/api-service';

export default function Page() {
  const t = useTrans('label.sales_managements,otr.common');
  const params = useParams();
  const formId = params.formId?.toString() || '';
  const opportunityId = params.managementId?.toString() || '';
  const [configId, setConfigId] = useState('');
  const [formAttributes, setFormAttributes] = useState<any[]>([]);
  const [_, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchTypeConfig = async () => {
      if (!formId) return;
      try {
        setIsLoading(true);
        setFormAttributes([]);
        const configResponse = await getAllOpportunityTypeConfig(formId, 'ONBOARDING');
        console.log('configResponse', configResponse);

        const FormId = configResponse?.is_success ? configResponse.result.form_id : '';
        const config_id = configResponse?.is_success ? configResponse.result.config_id : '';
        setConfigId(config_id);
        const attributesResponse = await getAllOpportunityTypeFormAttributes(FormId);
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
    try {
      const response = await uploadExcelToJson(file);
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
        backUrl={`/crm/a/sales-managements/${opportunityId}?t=opp-type&f=board`}
        title={t('info_upload')}
        mappingFields={formAttributes}
        onFileUpload={handleFileUpload}
        onMappingSubmit={(mappingData: any) => handleMappingSubmit(mappingData)}
        opportunityId={opportunityId}
      />
    </div>
  );
}
