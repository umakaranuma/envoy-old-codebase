import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string };

export async function getAllIncentiveSetupData(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/incentive-setups?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function deleteIncentiveSetup(id: string) {
  const response = await sendRequest({
    url: `${process.env.FINANCE_PROXY_PREFIX}/api/incentive-setups/${id}`,
    method: 'DELETE',
  });
  return responseHandling(response);
}

// export async function getAllRewardType(params: params) {
//   const queryString = new URLSearchParams(params).toString();

//   return responseHandling(
//     await sendRequest({
//       url: `${process.env.FINANCE_PROXY_PREFIX}/api/reward-types?${queryString}`,
//       method: 'GET',
//     }),
//   );
// }

export async function getAllRepeationType(params: params) {
  const queryString = new URLSearchParams(params).toString();

  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/repetition-types?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getAllIncentiveBaseField(params: params) {
  const queryString = new URLSearchParams(params).toString();

  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/incentive-base-fields?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getAllPerformanceField() {
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/performance-field-definitions`,
      method: 'GET',
    }),
  );
}

export async function getAllAsyncSelect(params: params, prefix: string, apiUrl: string) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${prefix}/${apiUrl}?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function createIncentiveSetup(formData: any) {
  const response = await sendRequest({
    url: `${process.env.FINANCE_PROXY_PREFIX}/api/incentive-setups`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getIncentiveSetupById(id: string) {
  const response = await sendRequest({
    url: `${process.env.FINANCE_PROXY_PREFIX}/api/incentive-setups/${id}`,
    method: 'GET',
  });
  return responseHandling(response);
}

export async function updateIncentiveSetup(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.FINANCE_PROXY_PREFIX}/api/incentive-setups/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}
