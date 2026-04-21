import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string; ids?: string };

export async function chartOfAccounts(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/chart-of-accounts?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOnechartOfAccounts(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/chart-of-accounts/${id}`,
      method: 'GET',
    }),
  );
}

export async function updatechartOfAccounts(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.FINANCE_PROXY_PREFIX}/api/chart-of-accounts/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function createchartOfAccounts(formData: any) {
  const response = await sendRequest({
    url: `${process.env.FINANCE_PROXY_PREFIX}/api/chart-of-accounts`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function deletechartOfAccounts(id: string) {
  const response = await sendRequest({
    url: `${process.env.FINANCE_PROXY_PREFIX}/api/chart-of-accounts/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function cashFlowStatements(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/cash-flow-journal?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function journalEntries(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/journal-entries?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function generalLedger(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/general-ledger/account-balances?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function debtorAgingSummaryReport(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/debtor-aging?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function commissionEarned(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/commission-earned?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function commissionGiven(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/commission-given?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function policyMade(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/policies-made?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function salesReport(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/sales-report?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function deleteSample(id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/groups/${id}`,
    method: 'DELETE',
  });
  return responseHandling(response);
}
