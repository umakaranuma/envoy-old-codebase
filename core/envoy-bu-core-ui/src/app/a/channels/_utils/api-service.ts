import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string };

export async function getAllChannels(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/channels?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOneChannels(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/channels/${id}`,
      method: 'GET',
    }),
  );
}

export async function createChannels(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/channels`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function updateChannels(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/channels/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function deleteChannels(id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/channels/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}
