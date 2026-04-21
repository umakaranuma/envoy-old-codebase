import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type params = {
  search?: string;
  page?: string;
  limit?: string;
  sort_by?: string;
  sort_dir?: string;
  filters?: string;
  end_date?: string;
  start_date?: string;
  agent_id?: string;
  insurer_id?: string;
  status?: string;
  download?: string;
  negative_outstanding?: string;
  settlement_id?: string;
};

export async function getBrokerageRevenuesPayments(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/brokerage-commissions?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getMultiAgentRevenuesPayments(params: params, abortDuplicate?: boolean, formData?: any) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/multi-agent-commission-list?${queryString}`,
      method: 'POST',
      abortDuplicate: abortDuplicate,
      data: formData,
    }),
  );
}
export async function getMultiBrokerageRevenuesPayments(params: params, abortDuplicate: boolean, formData: any) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/multi-brokerage-commission-list?${queryString}`,
      method: 'POST',
      abortDuplicate: abortDuplicate,
      data: formData,
    }),
  );
}

export async function getAgentCommissionPayments(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/agent-commissions?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getMyCommissionPayments(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/my-commissions?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllCommissionHistory(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/brokerage-commission-settlements?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOneCommissionHistoryCalculated(params: params, id: any, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/brokerage-commission/${id}/settlements?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOneCommissionHistoryDeductible(params: params, id: any, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/brokerage-commission/${id}/outstanding?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAgentCommissionTotals(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/agent-commissions/totals?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAgentCommissionSummaryTotals(params: params, abortDuplicate: boolean, formData: any) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/multi-agent-commission-totals?${queryString}`,
      method: 'POST',
      abortDuplicate: abortDuplicate,
      data: formData,
    }),
  );
}

export async function getInsurerCommissionSummaryTotals(params: params, abortDuplicate: boolean, formData: any) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/multi-brokerage-commission-totals?${queryString}`,
      method: 'POST',
      abortDuplicate: abortDuplicate,
      data: formData,
    }),
  );
}

export async function settleBrokerageCommission(formData: any) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/brokerage-commission-settlements`,
      method: 'POST',
      abortDuplicate: false,
      data: formData,
    }),
  );
}

export async function getBrokerCommissionTotals(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/brokerage-commissions/totals?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllUsers(params: params) {
  const queryString = new URLSearchParams(params).toString();

  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/users?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getOnePayments(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/payments/${id}`,
      method: 'GET',
    }),
  );
}

export async function createPayments(formData: any) {
  const response = await sendRequest({
    url: `${process.env.FINANCE_PROXY_PREFIX}/api/payments`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function updatePayments(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.FINANCE_PROXY_PREFIX}/api/payments/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function deletePayments(id: string) {
  const response = await sendRequest({
    url: `${process.env.FINANCE_PROXY_PREFIX}/api/payments/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function getMyCommissionTotals(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/my-commissions/totals?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function makeAgentCommission(formData: any) {
  const response = await sendRequest({
    url: `${process.env.FINANCE_PROXY_PREFIX}/api/agent-commission-payments`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function addSettlement(formData: any, id: any) {
  const response = await sendRequest({
    url: `${process.env.FINANCE_PROXY_PREFIX}/api/agent-commission-payments/${id}`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getOneAgentCommissionSettlements(commission_id: string, abortDuplicate?: boolean) {
  const response = await sendRequest({
    url: `${process.env.FINANCE_PROXY_PREFIX}/api/agent-commissions/${commission_id}`,
    method: 'GET',
    abortDuplicate: abortDuplicate,
  });

  return responseHandling(response);
}

export async function getAllSingleAgentCommison(params: params, commission_id: string, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/commission/${commission_id}/payments/?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}
