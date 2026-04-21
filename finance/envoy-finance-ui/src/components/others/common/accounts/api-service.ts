import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string; ids?: string };

export async function createCustomers(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/customers`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function createCustomerContacts(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/customers/${id}/contacts`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function createContact(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/contacts`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getAllCustomers(params: params, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/customers?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

type GParams = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string; ids?: string };
export async function getAllContacts(params: GParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/contacts?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}
