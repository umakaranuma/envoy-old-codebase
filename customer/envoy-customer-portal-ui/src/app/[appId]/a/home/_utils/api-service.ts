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
};

export async function getPolicyInfo(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/${id}/policy-info`,
      method: 'GET',
    }),
  );
}

export async function getAllIssuedPolicies(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/issued-policies?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function CreateClaim(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/claims`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getAllRiskInfoByRiskType(params: GAParams, id: string, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/risk-values/${id}?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllRisksByPolicyBase(params: GAParams, policyBaseId: string, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/policy-base/${policyBaseId}/risk-types?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}
