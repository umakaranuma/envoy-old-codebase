import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string };

export async function getAllTaskTypes(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/task-types?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function createTaskTypes(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/task-types`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getOneTaskTypes(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/task-types/${id}`,
      method: 'GET',
    }),
  );
}

export async function updateTaskTypes(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/task-types/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function deleteTaskTypes(id: string) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/task-types/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}
