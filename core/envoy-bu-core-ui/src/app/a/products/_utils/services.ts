import {
  getAllInsurerProducts,
  getAllNativeProducts,
  getInsurerProductCoverages,
  getAllProductDocument,
  getAllProductGroups,
  getAllProductTeam,
  getAllTeam,
  getInsurerProductDocuments,
  getInsurerProductsByNativeProduct,
  getOpportunityProducts,
  getOpportunityTypes,
  getProductsByVendor,
  getVendorsByOpportunityType,
  getInsurers,
  getCurrencies,
  getAllProductGrpProduct,
  getAllProductGrpTeam,
  getAllCategories,
  getAllCurrencies,
} from './api-service';

//Insurer product api start
export async function fetchInsurerProductsTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await getAllInsurerProducts(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: tableState.filters,
    },
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchInsurerProductCoverageTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any, product_id: string) {
  const response = await getInsurerProductCoverages(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: tableState.filters,
    },
    product_id,
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchPInsurerroductDocumentTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState, type }: any, product_id: string) {
  const response = await getInsurerProductDocuments(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      type: type,
      filters: tableState.filters,
    },
    product_id,
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllInsurerProducts(searchValue: any, currentPage: any) {
  const response = await getAllInsurerProducts({ search: searchValue, page: currentPage }, false);

  return response.result.data || [];
}

export async function fetchAllCategories(searchValue: any, currentPage: any) {
  const response = await getAllCategories({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

////Insurer product api end

//Native product api start
export async function fetchNativeProductsTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await getAllNativeProducts(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: tableState.filters,
    },
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchInsurerProductsByNativeProductTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState, nativeProductId }: any) {
  const response = await getInsurerProductsByNativeProduct(nativeProductId, {
    search: searchValue.toLowerCase(),
    page: currentPage,
    limit: itemsPerPage,
    sort_by: sortBy,
    sort_dir: sortDir,
    filters: tableState.filters,
  });

  if (response?.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
  return { data: [], dataLength: 0 };
}

export async function fetchProductTeamTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any, product_id: string) {
  const response = await getAllProductTeam(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: tableState.filters,
    },
    product_id,
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchProductCoverageTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any, product_id: string) {
  const response = await getInsurerProductCoverages(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: tableState.filters,
    },
    product_id,
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchProductDocumentTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState, type }: any, product_id: string) {
  const response = await getAllProductDocument(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      type: type,
      filters: tableState.filters,
    },
    product_id,
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllNativProduct(searchValue: any, currentPage: any) {
  const response = await getAllNativeProducts({ search: searchValue, page: currentPage }, false);

  return response.result.data || [];
}

//Native product api end

//Native product group api start
export async function fetchProductGroupsTableData({ searchValue, currentPage, itemsPerPage }: any) {
  const response = await getAllProductGroups(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
    },
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchProductGrpProductTableData({ searchValue, currentPage, itemsPerPage, grpId }: any) {
  const response = await getAllProductGrpProduct(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
    },
    true,
    grpId,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchProductGrpTeamTableData({ searchValue, currentPage, itemsPerPage, grpId }: any) {
  const response = await getAllProductGrpTeam(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
    },
    true,
    grpId,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}
//Native product group api end

export async function fetchAllTeamsDropdown(searchValue: any, currentPage: any) {
  const response = await getAllTeam({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function getAllVendors(searchValue: string, currentPage: number, opportunityTypeId: string) {
  const response = await getVendorsByOpportunityType(opportunityTypeId, { search: searchValue, page: currentPage.toString() });

  return response.result || [];
}

export async function getAllProducts(searchValue: string, currentPage: number, category_id: string, insurerProduct: any) {
  let response;
  if (insurerProduct?.vendor_id) {
    response = await getProductsByVendor({ search: searchValue, page: currentPage.toString() }, category_id, insurerProduct.vendor_id);
    return response.result || [];
  } else {
    response = await getOpportunityProducts(category_id, { search: searchValue, page: currentPage.toString() });
    return response.result.data || [];
  }
}

export async function fetchOpportunityTypes(searchValue: any, currentPage: any) {
  const response = await getOpportunityTypes({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchInsurers(searchValue: any, currentPage: any) {
  const response = await getInsurers({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchCurrencies(searchValue: any, currentPage: any) {
  const response = await getCurrencies({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchallNativeProducts(searchValue: any, currentPage: any) {
  const response = await getAllNativeProducts({ search: searchValue, page: currentPage }, false);

  return response.result.data || [];
}

export async function fetchAllCurrency(searchValue: any, currentPage: any) {
  const response = await getAllCurrencies({ search: searchValue, page: currentPage });

  return response.result.data || [];
}
