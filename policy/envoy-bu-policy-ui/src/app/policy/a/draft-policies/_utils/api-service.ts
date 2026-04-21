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
};

export async function getAllDraftPolicies(params: GAParams, abortDuplicate: boolean = true) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/draft-policies?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOneDraftPolicy(id: string) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/draft-policies/${id}`,
    method: 'GET',
  });

  return responseHandling(response);
}
