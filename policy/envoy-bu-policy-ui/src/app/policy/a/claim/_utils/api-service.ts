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
  status_type?: string;
};

export async function getAllClaims(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/claims?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllCustomersForClaims(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/claims/customers?fields=additional&${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllPoliciesOfCustomer(params: GAParams, customerId: any, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/claims/customers/${customerId}/policies?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getPolicyInfo(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/claims/${id}/policy-info`,
      method: 'GET',
    }),
  );
}

export async function CreateClaim(formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/claims`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getOneClaim(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/claims/${id}`,
      method: 'GET',
    }),
  );
}

export async function updateEvaluation(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/claims/${id}/evaluation-info`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function getOneEvaluation(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/claims/${id}/evaluation-info`,
      method: 'GET',
    }),
  );
}

export async function getAllCLaimStatus() {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/statuses?module=claim`,
      method: 'GET',
    }),
  );
}

export async function changeClaimStatus(formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/claims/change-status`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function sendIntimationEmail(formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/claims/send-email`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getOneNote(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api//${id}`,
      method: 'GET',
    }),
  );
}

export async function updateNote(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api//${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function CreateEndorsementRequests(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function createInvoicePayment(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}
