import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';
import { IContactDetail } from './model';

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string; ids?: string };

export async function getAllPartners(params: params, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/service-providers?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function createPartner(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/service-providers`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getOnePartner(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/service-providers/${id}`,
      method: 'GET',
    }),
  );
}

export async function updatePartner(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/service-providers/${id}`,
    method: 'PUT',
    data: formData,
  });

  return responseHandling(response);
}

export async function deletePartner(id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/service-providers/${id}`,
    method: 'DELETE',
  });
  return responseHandling(response);
}

export async function getAllPartnerProduct(params: params, abortDuplicate: boolean = false, sp_id: string) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/service-provider/${sp_id}/products?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllPartnerRQuotation(params: params, abortDuplicate: boolean = false, sp_id: string) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/service-provider/${sp_id}/quotations?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllPartnerContact(params: params, abortDuplicate: boolean = false, sp_id: string) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/service-provider/${sp_id}/contacts?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function createPartnerContact(formData: IContactDetail, partnerId: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/service-provider/${partnerId}/contacts`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getOnePartnerContact(partnerId: string, contactId: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/service-provider/${partnerId}/contacts/${contactId}`,
      method: 'GET',
    }),
  );
}

export async function updatePartnerContact(formData: IContactDetail, partnerId: string, contactId: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/service-provider/${partnerId}/contacts/${contactId}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function deletePartnerContact(partnerId: string, contactId: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/service-provider/${partnerId}/contacts/${contactId}`,
    method: 'DELETE',
  });
  return responseHandling(response);
}
