import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string };

export async function getAllServiceRendered(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/service-renders?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllInvoiceStatus(params: params) {
  const queryString = new URLSearchParams(params).toString();

  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/service-renders/invoice-status?${queryString}`,
      method: 'GET',
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

export async function getAllServiceRenderTypes(params: params) {
  const queryString = new URLSearchParams(params).toString();

  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/service-renders/services?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getAllPaymentStatus(params: params) {
  const queryString = new URLSearchParams(params).toString();

  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/service-renders/payment-status?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getOneServiceRendered(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/service-renders/${id}`,
      method: 'GET',
    }),
  );
}

export async function getOneServiceRenderedFee(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/service-renders/service/${id}/fee`,
      method: 'GET',
    }),
  );
}

export async function createServiceRendered(formData: any) {
  const response = await sendRequest({
    url: `${process.env.FINANCE_PROXY_PREFIX}/api/service-renders`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function updateServiceRendered(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.FINANCE_PROXY_PREFIX}/api/service-renders/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function deleteServiceRendered(id: string) {
  const response = await sendRequest({
    url: `${process.env.FINANCE_PROXY_PREFIX}/api/service-renders/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function getAllInvoicePayments(params: params, id: string) {
  const queryString = new URLSearchParams(params).toString();

  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/service-renders/${id}/payments?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function serviceRenderPayment(formData: any, id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/service-renders/${id}/payments`,
      method: 'POST',
      data: formData,
    }),
  );
}
