import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type GAParams = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string; status?: string; type?: string };

export async function getAllForms(params: GAParams, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/forms?${queryString}`,
      method: 'GET',
      abortDuplicate,
    }),
  );
}

export async function createForm(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/forms`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getOneForm(id: string) {
  // Send HTTP request to fetch a single sample
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/forms/${id}`,
      method: 'GET',
    }),
  );
}

export async function updateForm(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/forms/${id}`,
    method: 'PUT',
    data: formData,
  });

  return responseHandling(response);
}

export async function deleteForm(id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/forms/${id}`,
    method: 'DELETE',
  });
  return responseHandling(response);
}

export async function getAllAttributesOfForms(params: GAParams, id: any) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/forms/${id}/attributes?${queryString}`,
      method: 'GET',
      // abortDuplicate,
    }),
  );
}

export async function createAttributeOfForm(id: any, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/forms/${id}/attributes`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getOneAttribute(formId: string, id: string) {
  // Send HTTP request to fetch a single sample
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/forms/${formId}/attributes/${id}`,
      method: 'GET',
    }),
  );
}

export async function updateAttribute(formId: string, id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/forms/${formId}/attributes/${id}`,
    method: 'PUT',
    data: formData,
  });

  return responseHandling(response);
}

export async function deleteAttribute(formId: string, id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/forms/${formId}/attributes/${id}`,
    method: 'DELETE',
  });
  return responseHandling(response);
}
