import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

export async function getFormsOfCustomer(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/templates/${id}`,
      method: 'GET',
    }),
  );
}

export async function getOneEvaluation(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/claims/${id}/evaluation-info`,
      method: 'GET',
    }),
  );
}

export async function getOneClaim(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/claims/${id}`,
      method: 'GET',
    }),
  );
}

export async function getFormTemplate(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/templates/${id}`,
      method: 'GET',
    }),
  );
}

export async function getNewPolicyFormTemplate(id: string, type: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/${id}/template?type=${type}`,
      method: 'GET',
    }),
  );
}
