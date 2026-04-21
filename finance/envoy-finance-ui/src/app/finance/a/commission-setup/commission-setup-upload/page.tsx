'use client';
import Upload from '@/components/upload/Upload';
import React from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
// import { toaster } from '@/helpers/services/toaster';
import { uploadExcelToJson, submitMapping } from '@/helpers/services/excelUploadCommonService';

export default function Page() {
  const t = useTrans('label.commission_setup,otr.common');

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

  function flattenCommissionData(data: any[]): any[] {
    const grouped: Record<string, any> = {};

    data.forEach((item) => {
      const key = JSON.stringify({
        product_identifier: item.product_id || item.product_name,
        native_product_identifier: item.native_product_id || item.native_product_name,
        insurer_identifier: item.insurer_id || item.insurer_name,
        transaction_type_identifier: item.transaction_type_id || item.transaction_type_name,
      });

      if (!grouped[key]) {
        grouped[key] = {
          product_id: item.product_id,
          product_name: item.product_name,
          native_product_id: item.native_product_id,
          native_product_name: item.native_product_name,
          insurer_id: item.insurer_id,
          insurer_name: item.insurer_name,
          transaction_type_id: item.transaction_type_id,
          transaction_type_name: item.transaction_type_name,
          sales_team_ids: item.sales_team_ids.toString(),
          sales_team_names: item.sales_team_names,
          agent_commission_percent: item.agent_commission_percent,
          brokerage_revenue_percent: item.brokerage_revenue_percent,
          commission_type: item.commission_type,
          revised_commission_percent: [],
        };
      }

      // Add revised commission percent if available
      if (item.revised_commission_percent_user_id || item.revised_commission_percent_team_id) {
        grouped[key].revised_commission_percent.push({
          user_id: item.revised_commission_percent_user_id,
          user_name: item.revised_commission_percent_user_name,
          team_id: item.revised_commission_percent_team_id,
          team_name: item.revised_commission_percent_team_name,
          value: item.revised_commission_percent_value,
          type: item.commission_type || 'fixed',
        });
      }
    });

    return Object.values(grouped);
  }

  const handleMappingSubmit = async (mapping: any) => {
    const apidata = flattenCommissionData(mapping?.data);
    console.log('apidata', mapping.data);
    console.log('apidata', apidata);

    try {
      const mappedData = {
        ...mapping,
        data: apidata,
        type: 'commission_setup',
      };
      const response = await submitMapping(mappedData);

      if (response.is_success) {
        return response;
      }
      // Handle error case if needed
    } catch (error) {
      console.error('Error submitting mapping:', error);
      // Handle error if needed
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

  const mappingFields = [
    'Native Product Id',
    'Native Product Name',
    'Product Id',
    'Product Name',
    'Insurer Id',
    'Insurer Name',
    'Transaction Type Id',
    'Transaction Type Name',
    'Commission Type',
    'Brokerage Revenue Percent',
    'Agent Commission Percent',
    'Sales Team Ids',
    'Sales Team Names',
    'Revised Commission Percent User Id',
    'Revised Commission Percent User Name',
    'Revised Commission Percent Team Id',
    'Revised Commission Percent Team Name',
    'Revised Commission Percent Value',
  ];

  return (
    <div>
      <Upload
        isAllRequired={false}
        type="commission_setup"
        backUrl="/finance/a/commission-setup"
        title={t('commission_setup_upload')}
        mappingFields={mappingFields}
        onFileUpload={handleFileUpload}
        onMappingSubmit={handleMappingSubmit}
        onPreviewSubmit={handlePreviewSubmit}
      />
    </div>
  );
}
