import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string; type?: string };

// ProductGroups api start
export async function getAllProductGroups(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/product-groups?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllProductGrpProduct(params: params, abortDuplicate: boolean, id: string) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/product-groups/${id}/products?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllProductGrpTeam(params: params, abortDuplicate: boolean, id: string) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/product-groups/${id}/teams?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOneProductGroups(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/product-groups/${id}`,
      method: 'GET',
    }),
  );
}

export const createProductGroups = async (data: any) => {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/product-groups`,
    method: 'POST',
    data: data,
  });
  return responseHandling(response);
};

export async function updateProductGroups(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/product-groups/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export const deleteProductGroups = async (id: string) => {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/product-groups/${id}`,
    method: 'DELETE',
  });
  return responseHandling(response);
};

export async function updateProductGroupTeam(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/product-groups/${id}/teams`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function updateProductGroupProduct(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/product-groups/${id}/products`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export const deleteProductGroupTeam = async (grp_id: string, team_id: string) => {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/product-groups/${grp_id}/teams/${team_id}`,
    method: 'DELETE',
  });
  return responseHandling(response);
};

export const deleteProductGroupProduct = async (grp_id: string, product_id: string) => {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/product-groups/${grp_id}/products/${product_id}`,
    method: 'DELETE',
  });
  return responseHandling(response);
};

// InsurerProduct api start
export async function getAllInsurerProducts(params: params, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/insurer-products?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function createInsurerProducts(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/insurer-products`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function updateInsurerProducts(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/insurer-products/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function updateInsurerProductsNativeProductIds(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/insurer-product/${id}/native-product-mapping`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function deleteInsurerProduct(id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/insurer-products/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function getOneInsurerProducts(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/insurer-products/${id}`,
      method: 'GET',
    }),
  );
}

export async function getInsurerProductCoverages(params: params, id: string, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/insurer-products/${id}/coverage?${queryString}`,
    method: 'GET',
    abortDuplicate: abortDuplicate,
  });
  return responseHandling(response);
}

export async function createInsurerProductItem(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/insurer-products/${id}/coverage`,
    method: 'POST',
    data: formData,
    abortDuplicate: true,
  });
  return responseHandling(response);
}

export async function updateInsurerProductCoverage(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/product-coverage/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function deleteInsurerProductCoverage(id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/product-coverage/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function getInsurerProductDocuments(params: params, id: string, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/insurer-products/${id}/documents?${queryString}`,
    method: 'GET',
    abortDuplicate: abortDuplicate,
  });
  return responseHandling(response);
}

export async function createInsurerProductDocument(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/insurer-products/${id}/documents`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function updateInsurerProductDocument(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/product-document/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function deleteInsurerProductDocument(id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/product-document/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function getAllCategories(params: params) {
  const queryString = new URLSearchParams(params).toString();
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/product-categories?${queryString}`,
    method: 'GET',
    abortDuplicate: false,
  });
  return responseHandling(response);
}

// InsurerProduct api end

// NativeProducts api start
export async function getAllNativeProducts(params: params, abortDuplicate?: boolean) {
  const queryString = new URLSearchParams(params).toString();
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/native-products?${queryString}`,
    method: 'GET',
    abortDuplicate: abortDuplicate,
  });
  return responseHandling(response);
}

export async function getOneNativeProducts(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/native-products/${id}`,
      method: 'GET',
    }),
  );
}

export async function updateNativeProducts(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/native-products/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function updateNativeProductInsurerProducts(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/product/${id}/add-insurer-products`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export const createNativeProduct = async (data: any) => {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/native-products`,
    method: 'POST',
    data: data,
  });
  return responseHandling(response);
};

export const updateNativeProduct = async (id: string, data: any) => {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/native-products/${id}`,
    method: 'PUT',
    data: data,
  });
  return responseHandling(response);
};

export const getOneNativeProduct = async (id: string) => {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/native-products/${id}`,
      method: 'GET',
    }),
  );
};

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

export const deleteNativeProduct = async (id: string) => {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/native-products/${id}`,
    method: 'DELETE',
  });
  return responseHandling(response);
};

export const getOpportunityTypes = async (params?: params) => {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/opportunity-types?${queryString}`,
      method: 'GET',
    }),
  );
};

export const getVendorsByOpportunityType = async (opportunityTypeId: string, params?: params) => {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/opportunity-type/${opportunityTypeId}/vendors?${queryString}`,
      method: 'GET',
    }),
  );
};

export const getProductsByVendor = async (params: params, opportunityTypeId: string, vendorId: string) => {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/opportunity-type/${opportunityTypeId}/vendors/${vendorId}/products?${queryString}`,
      method: 'GET',
    }),
  );
};

export const getCoverageLevels = async () => {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/coverage-levels`,
      method: 'GET',
    }),
  );
};

export const deleteInsurerProductFromNative = async (nativeProductId: string, insurerProductId: string) => {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/native-product/${nativeProductId}/insurer-product/${insurerProductId}/remove`,
    method: 'DELETE',
  });
  return responseHandling(response);
};

export const getOpportunityProducts = async (opportunityTypeId: string, params?: params) => {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/opportunity-type/${opportunityTypeId}/products?${queryString}`,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
};

export async function getAllProductTeam(params: params, product_id: string, abortDuplicate: boolean) {
  console.log('CORE_API_URL: ', process.env.CORE_API_URL);
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/product/${product_id}/teams?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllProductCoverage(params: params, product_id: string, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/product/${product_id}/coverages?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllProductDocument(params: params, product_id: string, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/product/${product_id}/documents?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllTeam(params: params) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/teams?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function createProductTeam(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/product/${id}/teams`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function deleteProductTeam(id: string, team_id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/product/${id}/teams/${team_id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export const getInsurers = async (params: params) => {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/service-providers?${queryString}`,
      method: 'GET',
    }),
  );
};

export const getCurrencies = async (params: params) => {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/currencies?${queryString}`,
      method: 'GET',
    }),
  );
};

export async function getAllCurrencies(params: params) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/currencies?${queryString}`,
      method: 'GET',
    }),
  );
}
