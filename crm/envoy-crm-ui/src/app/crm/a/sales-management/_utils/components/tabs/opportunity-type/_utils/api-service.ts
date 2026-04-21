import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';
import { IExcelMappingResponse, IMappingSubmitData } from './model';

type GAParams = {
  search?: string;
  page?: string;
  limit?: string;
  sort_by?: string;
  sort_dir?: string;
  filters?: string;
  status?: string;
  type?: string;
  stage_id?: string;
  sales_agent_id?: string;
  ids?: string;
  opportunityId?: string;
  ignore?: string;
  fields?: string;
  customer_id?: string;
  risk_type_id?: any;
  policy_base_id?: string;
  lead_id?: string;
  stage?: string;
  group_id?: string;
  product_id?: string;
  risk_type_ids?: any;
  base_id?: string;
};

export const submitExcelData = async (opp_id: string, config_id: string, data: IMappingSubmitData): Promise<any> => {
  try {
    const response = await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${opp_id}/form-config/${config_id}/bulk-submit`,
      method: 'POST',
      data: data,
    });
    return responseHandling(response);
  } catch (error) {
    console.error('Error submitting mapping:', error);
    throw error;
  }
};

export const uploadExcelToJson = async (file: File): Promise<IExcelMappingResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${process.env.UTILITIES_PROXY_PREFIX}/api/app/export/excel-to-json`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed with status ${response.status}`);
    }

    const result = await response.json();

    if (result.success) {
      return result;
    } else {
      throw new Error(result.message || 'Failed to upload file');
    }
  } catch (error) {
    console.error('Error uploading Excel file:', error);
    throw error;
  }
};

export async function getBulkUploadExcel(params: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/policy/risk-export?${queryString}`,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
}

export async function bulkUpload(formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/policy/process-risk-excel`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}
