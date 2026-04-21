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
  lead_id?: string;
};

export async function getAllRisks(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/policy/risk?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllLeadsByCustomer(params: GAParams, customerId: string, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/policy/lead-by-customer/${customerId}?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllRisksByLead(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/risk-types?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllRisksByPolicyBase(params: GAParams, policyBaseId: string, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/policy/policy-base/${policyBaseId}/risk-types?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getRiskRegisterFormTemplate(leadId: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/policy/risk-form/${leadId}`,
      method: 'GET',
    }),
  );
}

export async function CreateRisk(formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/policy/risk`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getOneRisk(riskId: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/policy/risk-detail/${riskId}`,
      method: 'GET',
    }),
  );
}

export async function updateOneRisk(riskId: string, formData: any) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/policy/risk-detail/${riskId}`,
      method: 'PUT',
      data: formData,
    }),
  );
}

export async function deleteRisk(id: string) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/policy/risk-detail/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function getAllRisksHistories(params: GAParams, riskId: string, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/policy/risk/${riskId}/submission-values?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}
