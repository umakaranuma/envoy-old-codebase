import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string };

export async function getAllRoles(params: params, abortDuplicate: boolean) {
  console.log('CORE_API_URL: ', process.env.CORE_API_URL);
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/roles?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOneRoles(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/roles/${id}`,
      method: 'GET',
    }),
  );
}

export async function createRoles(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/roles`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function updateRoles(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/roles/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function deleteRoles(id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/roles/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function getAllPermissions(key: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/permissions?module_key=${key}`,
      method: 'GET',
    }),
  );
}

export async function storeRolePermissions(id: string, data: { permissions: number[] }) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/roles/${id}/permissions`,
    method: 'POST',
    data,
  });

  return responseHandling(response);
}

export async function getAllRolePermissions(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/roles/${id}/permissions`,
      method: 'GET',
    }),
  );
}
