import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string; type?: string };

export async function getAllCommissionSetupsData(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/commission-setups?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function createCommissionSetup(formData: any) {
  const response = await sendRequest({
    url: `${process.env.FINANCE_PROXY_PREFIX}/api/commission-setups/multi`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getOneCommssionSetup(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/commission-setups/${id}`,
      method: 'GET',
    }),
  );
}

export async function updateCommissionSetup(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.FINANCE_PROXY_PREFIX}/api/commission-setups/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function deleteCommissionSetup(id: string) {
  const response = await sendRequest({
    url: `${process.env.FINANCE_PROXY_PREFIX}/api/commission-setups/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function getAllProducts(params: params) {
  const queryString = new URLSearchParams(params).toString();

  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/native-products?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getAllInsurer(params: params) {
  const queryString = new URLSearchParams(params).toString();

  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/insurers?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getAllTransactionType(params: params) {
  const queryString = new URLSearchParams(params).toString();

  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/transaction-types?${queryString}`,
      method: 'GET',
    }),
  );
}
export async function getAllTeams(params: params) {
  const queryString = new URLSearchParams(params).toString();

  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/teams?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getOneTeams(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/teams/${id}`,
      method: 'GET',
    }),
  );
}

export const getInsurerProductsByNativeProduct = async (nativeProductId: string, params: params) => {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/native-products/${nativeProductId}/products?${queryString}`,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
};

export const getInsurerProductTeamTableData = async (nativeProductId: string, params: params) => {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/native-products/${nativeProductId}/products?${queryString}`,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
};

export const getNativeProductTeamTableData = async (nativeProductId: string, params?: params) => {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/product/${nativeProductId}/teams?${queryString}`,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
};

export const getTeamTableData = async (teamId: string, params: params) => {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/teams/${teamId}?${queryString}`,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
};

export const getSalesTeamMemberTableData = async (params: params, setupId: string, teamId: string) => {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.FINANCE_PROXY_PREFIX}/api/commission-setups/${setupId}/teams/${teamId}?${queryString}`,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
};

export async function updateRCommission(setupId: string, teamId: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.FINANCE_PROXY_PREFIX}/api/commission-setups/${setupId}/teams/${teamId}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function getAllProductGrps(params: params) {
  const queryString = new URLSearchParams(params).toString();

  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/product-groups?${queryString}`,
      method: 'GET',
    }),
  );
}

export const getProductGrpInsurer = async (productGrpId: string, params: params) => {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/product-group/${productGrpId}/insurers?${queryString}`,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
};

export const getProductGroupTeamTableData = async (grpId: string, insurenceId: string, params?: params) => {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/product-group/${grpId}/insurence/${insurenceId}/teams?${queryString}`,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
};
