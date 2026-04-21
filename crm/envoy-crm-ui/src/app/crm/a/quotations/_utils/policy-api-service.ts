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
  service_provider_id?: string;
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

export async function getProductDocuments(params: GAParams, product_id: string) {
  const queryString = new URLSearchParams(params).toString();
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/insurer-products/${product_id}/documents-enhanced?${queryString}`,
    method: 'GET',
  });

  return responseHandling(response);
}

export async function createPolicyRequest(formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/policy-request`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function policyRequestEmail(formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/policy-approval`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}
