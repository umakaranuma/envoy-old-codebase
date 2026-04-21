import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type GAParams = {
  search?: string;
  page?: string;
  limit?: string;
  sort_by?: string;
  sort_dir?: string;
  filters?: string;
  status?: string;
  type?: string;
  stage_id?: string;
  sales_agent_id?: string;
  ids?: string;
  read_status?: string;
  filter?: string;
};

export async function getAllNotification(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/all-notifications?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function changeNotificationStatus(ids: any) {
  const response = await sendRequest({
    url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/read-notifications/${ids}`,
    method: 'POST',
  });
  return responseHandling(response);
}

export async function deleteNotification(id: string) {
  const response = await sendRequest({
    url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/notifications/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}
