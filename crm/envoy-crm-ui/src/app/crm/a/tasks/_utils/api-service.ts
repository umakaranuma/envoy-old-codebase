import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

// type GAParams = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string; status?: string; type?: string };
// const queryString = new URLSearchParams(params).toString();

export async function getAllTaskStatuses(assigneeId?: string, abortDuplicate: boolean = false) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/tasks-statuses?assigned_to=${assigneeId}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

type GAParams = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string; status?: string; type?: string; opportunity_id?: string };

export async function getAllAssigneeTasks(statusId: string, assigneeId: string, page: string, sort_by?: string, sort_dir?: string, fields?: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/tasks?assigned_to=${assigneeId}&task_status_id=${statusId}&page=${page}&sort_by=${sort_by}&sort_dir=${sort_dir}&fields=${fields}`,
      method: 'GET',
    }),
  );
}

export async function updateTaskStatus(taskId: string, formData: any) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/tasks/${taskId}/status`,
      method: 'PATCH',
      data: formData,
    }),
  );
}

export async function getAllAssigneTask(params: GAParams, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/tasks?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllTaskSatuses(params: GAParams, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/tasks-statuses?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllTaskStatusesOfTask(params: GAParams, id: any, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/tasks/${id}/status-histories?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllAssignees(params: GAParams, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/tasks-assignees?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllAssigneeHistories(params: GAParams, id: any, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/tasks/${id}/assignee-histories?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOneAssignedTask(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/tasks/${id}`,
      method: 'GET',
    }),
  );
}

export async function createAssignedTask(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/tasks`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function updateAssignedTask(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/tasks/${id}`,
    method: 'PUT',
    data: formData,
  });

  return responseHandling(response);
}

export async function deleteAssignedTask(id: string) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/tasks/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function deleteTaskConfigs(id: string) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/task-configs/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function getOneUser(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/users/${id}`,
      method: 'GET',
    }),
  );
}

export async function getOneTaskStatus(_id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/tasks-statuses`,
      method: 'GET',
    }),
  );
}

export async function getAllInteractionOfTask(params: GAParams, id: string, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/tasks/${id}/interactions?${queryString}`,
      method: 'GET',
      abortDuplicate,
    }),
  );
}

export async function createInteraction(id: any, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/tasks/${id}/interactions`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function deleteTaskInteraction(id: string, intId: string) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/tasks/${id}/interactions/${intId}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function getManyOpportunities(ids: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/tasks/opportunities/many?ids=${ids}`,
      method: 'GET',
    }),
  );
}

export async function changeTaskStatus(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/tasks/${id}/status`,
    method: 'PUT',
    data: formData,
  });

  return responseHandling(response);
}

export async function getAllTaskCalender(fromDate: string, toDate: string, id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/tasks/assignee/calendar?from_date=${fromDate}&to_date=${toDate}&assignee_id=${id}`,
      method: 'GET',
    }),
  );
}
