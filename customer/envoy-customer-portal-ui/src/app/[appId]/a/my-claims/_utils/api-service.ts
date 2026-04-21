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
};

export async function getAllClaims(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/claims?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOneClaimEvaluationInfo(claimId: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/claims/${claimId}/evaluation-info`,
      method: 'GET',
    }),
  );
}

export async function getOneClaimFNOLInfo(claimId: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/claims/${claimId}`,
      method: 'GET',
    }),
  );
}

export async function updateClaimFNOLInfo(claimId: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/claims/${claimId}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}
