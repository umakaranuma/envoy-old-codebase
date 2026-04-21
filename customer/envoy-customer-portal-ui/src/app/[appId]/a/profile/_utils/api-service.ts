import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string };

export async function getProfileMyDetails() {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/profile/personal-info`,
      method: 'GET',
    }),
  );
}

export async function updateProfileInfo(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/profile/personal-info`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function getUserLogs() {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/login-history`,
      method: 'GET',
    }),
  );
}

export async function getUserEmailInfo() {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/profile/contact-email`,
      method: 'GET',
    }),
  );
}

export async function updateEmailInfo(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/profile/contact-email`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function getAllBillingInfo(params: params, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/policy-settlement?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getNotificationSettingInfo() {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/notification-settings`,
      method: 'GET',
    }),
  );
}

export async function updateNotificationInfo(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/notification-settings`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}
