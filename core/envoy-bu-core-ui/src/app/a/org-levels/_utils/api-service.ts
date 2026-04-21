import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string };

export async function getAllOrgLevel(params: params, abortDuplicate: boolean) {
  console.log('CORE_API_URL: ', process.env.CORE_API_URL);
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/organization-levels?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOneOrgLevel(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/organization-levels/${id}`,
      method: 'GET',
    }),
  );
}

export async function createOrgLevel(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/organization-levels`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function updateOrgLevel(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/organization-levels/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function deleteOrgLevel(id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/organization-levels/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}
