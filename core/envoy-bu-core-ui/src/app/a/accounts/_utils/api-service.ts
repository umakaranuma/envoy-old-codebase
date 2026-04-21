import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string; ids?: string; ignore?: string };

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

export async function getAllCustomersHierarchies(id: string) {
  // const queryString = new URLSearchParams().toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/customers/hierarchies?node_id=${id}`,
      method: 'GET',
      // abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOneCustomers(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/customers/${id}`,
      method: 'GET',
    }),
  );
}

export async function createCustomers(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/customers`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function updateCustomers(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/customers/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function deleteCustomers(id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/customers/${id}`,
    method: 'DELETE',
  });
  return responseHandling(response);
}

export async function deleteHierarchies(id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/customers/${id}/hierarchies`,
    method: 'DELETE',
  });
  return responseHandling(response);
}

export async function createHierarchies(id: any, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/customers/${id}/hierarchies`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getAllCustomerContact(params: params, abortDuplicate: boolean, id: string) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/customers/${id}/contacts?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function deleteCustomerContact(id: string, contact_id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/customers/${id}/contacts/${contact_id}`,
    method: 'DELETE',
  });
  return responseHandling(response);
}

export async function setAsPrimaryCustomerContact(id: string, contact_id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/customers/${id}/contacts/${contact_id}/primary`,
    method: 'PATCH',
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

export async function getAllPrimaryContact(params: params, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/customers/primary-contact-person/many?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllAccTapData(params: params, abortDuplicate: boolean, id: string, tap: string) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/customers/${id}/${tap}?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getCustomerConfig(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/customers/${id}/email`,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
}
export async function saveCustomerConfig(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/customers/configure`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}
