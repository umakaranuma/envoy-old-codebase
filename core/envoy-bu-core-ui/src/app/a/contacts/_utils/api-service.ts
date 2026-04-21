import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string; ids?: string };

export async function getAllContacts(params: params, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/contacts?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOneContacts(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/contacts/${id}`,
      method: 'GET',
    }),
  );
}

export async function createContacts(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/contacts`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function updateContacts(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/contacts/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function deleteContacts(id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/contacts/${id}`,
    method: 'DELETE',
  });
  return responseHandling(response);
}

export async function createContactGroup(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/groups`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getAllContactGroups(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/groups?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

// Interactions

export async function getAllInteractions(id: string, params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/contacts/${id}/interactions?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function deleteContactGroup(id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/groups/${id}`,
    method: 'DELETE',
  });
  return responseHandling(response);
}

export async function getAvailableContacts(params: params, abortDuplicate: boolean, id: any) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/groups/${id}/assignable-contacts?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllContactsOfGroup(params: params, id: any) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/groups/${id}/contacts?${queryString}`,
      method: 'GET',
      // abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOneGroup(id: any) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/groups/${id}`,
      method: 'GET',
    }),
  );
}

export async function getOneInteraction(contactId: string, id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/contacts/${contactId}/interactions/${id}`,
      method: 'GET',
    }),
  );
}

export async function updateGeneralContactGroup(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/groups/${id}`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function addContactsOfGroup(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/groups/${id}/contacts`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function deleteContactsOfGroup(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/groups/${id}/contacts`,
    method: 'DELETE',
    data: formData,
  });
  return responseHandling(response);
}

export async function getAllMergeableContacts(params: params, abortDuplicate: boolean, ids: any) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/contacts/relations?ids=${ids}&${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function mergeContacts(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/contacts/merge-contacts`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getMergeAccounts(params: params, abortDuplicate: boolean, id: any) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/contacts/${id}/customers?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function deleteMergeAccounts(contact_id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/contacts/merge-contacts`,
    method: 'DELETE',
    data: { contact_id },
  });
  return responseHandling(response);
}
