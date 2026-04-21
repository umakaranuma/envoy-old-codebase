import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

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
  agent_Id?: string;
  product_group_id?: string;
  manager_id?: string;
};

export async function deleteTypeForm(formId: string, id: string) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types/${id}/forms/${formId}`,
    method: 'DELETE',
  });
  return responseHandling(response);
}

export async function createTypesOfForm(id: any, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types/${id}/forms`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getOneForm(formId: string, id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types/${formId}/forms/${id}`,
      method: 'GET',
    }),
  );
}

export async function updateTypeForm(formId: string, id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types/${formId}/forms/${id}`,
    method: 'PUT',
    data: formData,
  });

  return responseHandling(response);
}

export async function getAllForms(params: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/forms?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function FormsTableData(params: GAParams, id: string) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types/${id}/forms?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getOneType(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types/${id}`,
      method: 'GET',
    }),
  );
}

export async function getAllUsers(params: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/users?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getAllSalesAgent(params: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/teams/sales-agents?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function createPolicyRequest(formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/policy-request`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getOnePolicyRequest(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/policy-request/${id}`,
      method: 'GET',
    }),
  );
}

export async function getAllProductTypes(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/risk-types?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllCoverages(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/coverage-types?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllPaymentTypes(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/payment-plans?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllInsurers(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/insurers?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllPolicyRequests(params: GAParams, abortDuplicate: boolean = true) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/policy-request?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function renewalPolicyRequest(id: any, formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/issued-policy-renewal/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function addPolicyRequest(id: any, formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/policy-requests/${id}/issued-policy`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function createIssuedPolicy(formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/issued-policy`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getAllOpportunities(params: GAParams, abortDuplicate: boolean = true) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/policy/qualified-opportunities?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllRiskInfoByRiskType(params: GAParams, id: string, abortDuplicate: boolean = true) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/risk-values/${id}?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export const submitExcelData = async (opp_id: string, config_id: string, data: any) => {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunities/${opp_id}/form-config/${config_id}/bulk-submit`,
    method: 'POST',
    data: data,
  });
  return responseHandling(response);
};

export const uploadExcelToJson = async (formData: any) => {
  const response = await sendRequest({
    url: `${process.env.UTILITIES_PROXY_PREFIX}/api/app/export/excel-to-json`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
};

export async function getAllProductsByType(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/products-filters?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getProductDocuments(params: GAParams, product_id: string) {
  const queryString = new URLSearchParams(params).toString();
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/insurer-products/${product_id}/documents-enhanced?${queryString}`,
    method: 'GET',
  });

  return responseHandling(response);
}

export async function getIssuedPolicyData(params: GAParams, abortDuplicate: boolean = true) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/issued-policies/all?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function policyRequestEmail(formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/policy-approval`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getPolicyRiskInfoFile(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/policy-base/${id}/export-risks`,
      method: 'GET',
    }),
  );
}

export async function getAllChatMsg(params: GAParams, abortDuplicate: boolean, policy_id: string) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/policy/${policy_id}/chat-messages?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function createMsg(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/chatmail/send`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getSyncChatMsg(abortDuplicate: boolean, policy_id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/policy/${policy_id}/sync-conversations`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function extractDocs(formData: any, request_policy_id: string) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/policy/request-policy/${request_policy_id}/download-docs`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function getPolicyRequestExtractedData(policy_request_id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}//api/policy/request-policy/${policy_request_id}/data-analysis`,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
}

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

export async function getAccountManager(params: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/teams/account-managers?${queryString}`,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
}
