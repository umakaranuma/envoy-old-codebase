import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type GAParams = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string; status?: string; type?: string; opportunity_id?: string; ignore?: string };

export async function deleteTaskConfigs(id: string) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/task-configs/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function getAllTaskConfigs(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/task-configs?${queryString}`,
    method: 'GET',
    abortDuplicate: abortDuplicate,
  });

  return responseHandling(response);
}

export async function getOneTaskConfigs(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/task-configs/${id}`,
      method: 'GET',
    }),
  );
}

export async function updateTaskConfigs(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/task-configs/${id}`,
    method: 'PUT',
    data: formData,
  });

  return responseHandling(response);
}

export async function getAllTaskTypes(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/task-types?${queryString}`,
      method: 'GET',
      abortDuplicate,
    }),
  );
}

export async function getOpportunityStages(params?: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-statuses?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function createTaskConfigs(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/task-configs`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}
