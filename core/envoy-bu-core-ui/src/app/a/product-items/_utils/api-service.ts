import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string; ids?: string };

export async function getAllProductItems(params: params, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/product-items?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function createProductItem(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/product-items`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getOneProductItem(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/product-items/${id}`,
      method: 'GET',
    }),
  );
}

export async function updateProductItem(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/product-items/${id}`,
    method: 'PUT',
    data: formData,
  });

  return responseHandling(response);
}

export async function deleteProductItem(id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/product-items/${id}`,
    method: 'DELETE',
  });
  return responseHandling(response);
}
