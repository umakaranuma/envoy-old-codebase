import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type GAParams = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string; status?: string; type?: string; role?: string };

export async function getAllUser(params: GAParams, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/users?${queryString}`,
      method: 'GET',
      abortDuplicate,
    }),
  );
}

export async function getOneUser(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/users/${id}`,
      method: 'GET',
    }),
  );
}

export async function getAllInvitations(params: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/invitations?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getAllUserRoles(params: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/roles?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function inviteUser(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/users/invite`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function cancelInvitation(id: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/invitations/${id}/cancel`,
    method: 'POST',
  });
  return responseHandling(response);
}

export async function resendInvitation(id: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/invitations/${id}/resend`,
    method: 'POST',
  });
  return responseHandling(response);
}

export async function updateUser(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/users/${id}`,
    method: 'PUT',
    data: formData,
  });

  return responseHandling(response);
}

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string; ids?: string; ignore?: string };

export async function getAllSalesTarget(params: params, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/user-sales-targets?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

type STParams = {
  search?: string;
  page?: string;
  limit?: string;
  sort_by?: string;
  sort_dir?: string;
  filters?: string;
  status?: string;
  type?: string;
  userId?: string;
  year?: string;
  month?: string;
};

export async function getAllUserSalesTarget(params: STParams, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/sales-targets?${queryString}`,
      method: 'GET',
      abortDuplicate,
    }),
  );
}

export async function getAllUserYearSalesTarget(params: STParams, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/year-sales-target?${queryString}`,
      method: 'GET',
      abortDuplicate,
    }),
  );
}

export async function getOneSalesTarget(params: any) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/sales-targets?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getOneSalesTargetSingle(params: any) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/sales-target-single?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function createSalesTarget(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/sales-targets`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getAllSalesTargetCharts(params: STParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/user-sales-target-graph?${queryString}`,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
}

export async function addMemberInTeam(formData: any, team_id: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/teams/${team_id}/users`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getAllTeam(params: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/teams?${queryString}`,
      method: 'GET',
    }),
  );
}
