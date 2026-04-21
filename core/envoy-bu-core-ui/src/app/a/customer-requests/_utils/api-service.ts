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

export async function getAllCustomerRequests(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/customer-requests/by-type?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllCustomerPayments(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/customer-payments?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOneCustomerRequest(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/customer-requests/${id}`,
      method: 'GET',
    }),
  );
}

export async function approveCustomerRequest(id: any, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/customer-requests/${id}/confirm`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function approveCustomerPaymentRequest(id: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/customer-payments/confirm`,
    method: 'POST',
    data: { customer_payment_id: id },
  });
  return responseHandling(response);
}
