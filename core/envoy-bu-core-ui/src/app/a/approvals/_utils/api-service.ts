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
  risk_type_id?: string;
  customer_id?: string;
  policy_base_id?: string;
  approval_id?: string;
};

export async function getAllApprovals(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/approvals?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOneApproval(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/approvals/${id}`,
      method: 'GET',
    }),
  );
}

export async function deleteApproval(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/approvals/${id}`,
      method: 'DELETE',
    }),
  );
}

export async function sendApproval(id: any, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/approvals/${id}/changes`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function updateApproval(id: any, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/approvals/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function findApprovalProcessAvailable(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/quotation-approval/entity/${id}`,
      method: 'GET',
    }),
  );
}

export async function getAllServiceProviders(params: GAParams, abortDuplicate: boolean = true) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/service-providers?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOpportunityInfoOfApproval(params: GAParams, riskTypeId: any) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/risk-values/${riskTypeId}?${queryString}`,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
}

export async function getOpportunityInfoElements(params: GAParams, approvalId: any) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/approvals/${approvalId}/risk-details?${queryString}`,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
}

export async function getAllOpportunityTypeConfig(opportunityTypeId: string, data_gethering_type: 'ONBOARDING') {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types/${opportunityTypeId}/form-config?data_gethering_type=${data_gethering_type}`,
    method: 'GET',
    abortDuplicate: true,
  });

  return responseHandling(response);
}

export async function getAllOpportunityTypeFormAttributes(formId: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/forms/${formId}/elements`,
    method: 'GET',
    abortDuplicate: true,
  });

  return responseHandling(response);
}
