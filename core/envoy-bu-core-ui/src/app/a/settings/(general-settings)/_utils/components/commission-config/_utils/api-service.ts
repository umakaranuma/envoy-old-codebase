import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

export async function getCommissionConfig() {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/settings/commission_config`,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
}

export async function updateCommissionConfig(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/settings/commission_config`,
    method: 'PATCH',
    data: formData,
  });
  return responseHandling(response);
}

export async function getApprovalPermissions() {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/settings/approval_permissions  `,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
}

export async function updateApprovalPermission(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/settings/approval_permissions`,
    method: 'PATCH',
    data: formData,
  });

  return responseHandling(response);
}
