import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type GAParams = {
  search?: string;
  page?: string;
  limit?: string;
  sort_by?: string;
  sort_dir?: string;
  filters?: string;
  status?: string;
  type?: string;
  ids?: string;
  read_status?: string;
  filter?: string;
};

export async function getAllUsers(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/users?${queryString}`,
      method: 'GET',
      abortDuplicate,
    }),
  );
}

export async function getAllEntities(params?: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/entities?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getAllCustomers(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/customers?${queryString}`,
      method: 'GET',
      abortDuplicate,
    }),
  );
}

export async function getAllContacts(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/contacts?${queryString}`,
      method: 'GET',
      abortDuplicate,
    }),
  );
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

export async function getAllTaskStatuses(params?: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/tasks-statuses?${queryString}`,
      method: 'GET',
      abortDuplicate,
    }),
  );
}

export async function getAllAuthUserPermissions(moduleKey: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_API_URL}/api/my-permissions?module_key=${moduleKey}`,
    method: 'GET',
  });

  return responseHandling(response);
}

export async function authUser(_token: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/me`,
    method: 'GET',
    // authorization: 'Bearer ' + token,
  });

  return responseHandling(response);
}

export async function getAppMenu() {
  const response = await sendRequest({
    url: `${process.env.CORE_BASE_URL}/api/configs/app-menu?module_key=FINANCE`,
    method: 'GET',
  });

  return response;
}

export async function getSetting(key: any, requestType: 'server' | 'client' = 'client') {
  return responseHandling(
    await sendRequest({
      url: `${requestType === 'server' ? process.env.CORE_API_URL : process.env.CORE_PROXY_PREFIX}/api/settings/${key}`,
      method: 'GET',
    }),
  );
}

export async function getAllNotification(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/all-notifications?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}
