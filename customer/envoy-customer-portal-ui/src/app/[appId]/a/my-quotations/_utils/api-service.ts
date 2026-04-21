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
  filter?: string;
};

export async function getAllQuotations(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/quotations?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllQuotationServiceProviders(params: GAParams, id: any, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/quotations/${id}/vendor-responses?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function confirmQuotation(id: string) {
  const response = await sendRequest({
    url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/send-quotations/${id}/confirm`,
    method: 'PUT',
  });
  return responseHandling(response);
}
