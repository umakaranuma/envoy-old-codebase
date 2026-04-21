import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string };

export async function getAllPayments(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/payments?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllInvoices(params: params) {
  const queryString = new URLSearchParams(params).toString();

  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/invoices?${queryString}`,
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

export async function getPaymentImportTemplate() {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/export/receipts-excel`,
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
