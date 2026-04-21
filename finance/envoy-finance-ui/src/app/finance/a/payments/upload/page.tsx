'use client';
import Upload from '@/components/upload/Upload';
import React from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
// import { toaster } from '@/helpers/services/toaster';
import { uploadExcelToJson, submitMapping } from '@/helpers/services/excelUploadCommonService';

export default function Page() {
  const t = useTrans('label.invoice,otr.common');

  const handleFileUpload = async (file: File) => {
    try {
      const response = await uploadExcelToJson(file);
      return response;
    } catch (error) {
      console.error('Error uploading file:', error);
      // toaster.error('Failed to upload file');
      throw error;
    }
  };

  const handleMappingSubmit = async (mapping: any) => {
    try {
      const response = await submitMapping({
        ...mapping,
        type: 'payments',
      });
      if (response.is_success) {
        return response;
      } else {
        // throw new Error(response.message || 'Failed to submit mapping');
      }
    } catch (error) {
      console.error('Error submitting mapping:', error);
      // toaster.error('Failed to submit mapping');
      // throw error;
    }
  };

  const handlePreviewSubmit = async (data: any) => {
    try {
      // TODO: Implement preview submission API call
      console.log('Preview submitted:', data);
      return Promise.resolve();
    } catch (error) {
      console.error('Error submitting preview:', error);
      // toaster.error('Failed to submit preview');
      throw error;
    }
  };

  const mappingFields = ['Receipt Number', 'Paid Amount', 'Insurer Policy Number', 'Insurer Invoice Id'];

  return (
    <div>
      <Upload
        type="payments"
        backUrl="/finance/a/payments"
        title={t('invoice_upload')}
        mappingFields={mappingFields}
        onFileUpload={handleFileUpload}
        onMappingSubmit={handleMappingSubmit}
        onPreviewSubmit={handlePreviewSubmit}
      />
    </div>
  );
}
