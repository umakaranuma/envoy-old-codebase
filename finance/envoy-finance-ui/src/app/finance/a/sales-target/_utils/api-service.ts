import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string };

export async function getAllAgentSalesTarget(params: params, abortDuplicate: boolean) {
  // Construct query string from parameters
  const queryString = new URLSearchParams(params).toString();

  // Send HTTP request to fetch all AgentSalesTarget
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/agent-sales-targets?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllTeamSalesTarget(params: params, abortDuplicate: boolean) {
  // Construct query string from parameters
  const queryString = new URLSearchParams(params).toString();

  // Send HTTP request to fetch all TeamSalesTarget
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/team-sales-targets?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllSalesTeam(params: params) {
  // Construct query string from parameters
  const queryString = new URLSearchParams(params).toString();

  // Send HTTP request to fetch all salesTeam
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/teams?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getAllAgent(params: params, formData: any) {
  // Construct query string from parameters
  const queryString = new URLSearchParams(params).toString();

  const response = await sendRequest({
    url: `${process.env.FINANCE_PROXY_PREFIX}/api/advanced-user-search?${queryString}`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function createSalesTarget(formData: any, activetab: string) {
  const endpoint = activetab === 'individual' ? `${process.env.FINANCE_PROXY_PREFIX}/api/agent-sales-targets` : `${process.env.FINANCE_PROXY_PREFIX}/api/team-sales-targets`;

  const response = await sendRequest({
    url: endpoint,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getOneSalesTarget(id: string, activetab: string) {
  const endpoint = activetab === 'individual' ? `${process.env.FINANCE_PROXY_PREFIX}/api/agent-sales-targets/${id}` : `${process.env.FINANCE_PROXY_PREFIX}/api/team-sales-targets/${id}`;

  return responseHandling(
    await sendRequest({
      url: endpoint,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
}

export async function updateSalesTarget(id: string, activetab: string, formData: any) {
  const endpoint = activetab === 'individual' ? `${process.env.FINANCE_PROXY_PREFIX}/api/agent-sales-targets/${id}` : `${process.env.FINANCE_PROXY_PREFIX}/api/team-sales-targets/${id}`;

  const response = await sendRequest({
    url: endpoint,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function deleteSalesTarget(id: string, activetab: string) {
  const endpoint = activetab === 'individual' ? `${process.env.FINANCE_PROXY_PREFIX}/api/agent-sales-targets/${id}` : `${process.env.FINANCE_PROXY_PREFIX}/api/team-sales-targets/${id}`;

  const response = await sendRequest({
    url: endpoint,
    method: 'DELETE',
  });

  return responseHandling(response);
}
