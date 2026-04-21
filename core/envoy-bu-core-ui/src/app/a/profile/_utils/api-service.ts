import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string };

export async function getAllJobtitle(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/job-titles?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOneJobTitle(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/job-titles/${id}`,
      method: 'GET',
    }),
  );
}

export async function createJobtitle(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/job-titles`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function updateJobTitle(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/job-titles/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function deleteJobTitle(id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/job-titles/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}
