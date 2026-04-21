import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string; type?: string };

export async function createSalesTeam(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/teams`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getAllTeams(params: params, abortDuplicate?: boolean) {
  const queryString = new URLSearchParams(params).toString();
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/teams?${queryString}`,
    method: 'GET',
    abortDuplicate: abortDuplicate,
  });
  return responseHandling(response);
}

export async function updateSalesTeam(id: any, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/teams/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function getOneTeam(id: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/teams/${id}`,
    method: 'GET',
  });
  return responseHandling(response);
}

export async function deleteTeam(id: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/teams/${id}`,
    method: 'DELETE',
  });
  return responseHandling(response);
}
