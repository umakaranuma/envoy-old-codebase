import { thousandSeparator } from '@/helpers/services/commonService';

export const formatCommissionValue = (value: number | string | undefined, type: string | undefined, currencyCode: string) => {
  if (!value || !type) return '-';
  const formattedValue = thousandSeparator(value);
  const isPercentage = type === 'percentage';
  return isPercentage ? `${formattedValue}%` : `${currencyCode} ${formattedValue}`;
};

import {
  getAllCommissionSetupsData,
  getAllInsurer,
  getAllProductGrps,
  getAllProducts,
  getAllTeams,
  getAllTransactionType,
  getInsurerProductsByNativeProduct,
  getInsurerProductTeamTableData,
  getNativeProductTeamTableData,
  getOneTeams,
  getProductGroupTeamTableData,
  getProductGrpInsurer,
  getSalesTeamMemberTableData,
  getTeamTableData,
} from './api-service';

export async function fetchAllCommissionData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tab }: any) {
  const response = await getAllCommissionSetupsData(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      type: tab,
    },
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllProductsData(searchValue: any, currentPage: any) {
  const response = await getAllProducts({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllProductGroups(searchValue: any, currentPage: any) {
  const response = await getAllProductGrps({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllInsurerData(searchValue: any, currentPage: any) {
  const response = await getAllInsurer({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllTeamsData(searchValue: any, currentPage: any) {
  const response = await getAllTeams({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllTeamTableData(salesTeamId: string) {
  const response = await getOneTeams(salesTeamId);

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllTransationTypeData(searchValue: any, currentPage: any) {
  const response = await getAllTransactionType({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchInsurerProductsByNativeProduct(searchValue: any, currentPage: any, nativeProductId: string) {
  const response = await getInsurerProductsByNativeProduct(nativeProductId, { search: searchValue, page: currentPage });

  return response.result.data || [];
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

export async function fetchInsurerProductTeamTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState, nativeProductId }: any) {
  const response = await getInsurerProductTeamTableData(nativeProductId, {
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

export async function fetchNativeProductTeamTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState, nativeProductId }: any) {
  const response = await getNativeProductTeamTableData(nativeProductId, {
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

export async function fetchTeamTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState, teamId }: any) {
  const response = await getTeamTableData(teamId, {
    search: searchValue.toLowerCase(),
    page: currentPage,
    limit: itemsPerPage,
    sort_by: sortBy,
    sort_dir: sortDir,
    filters: tableState.filters,
  });

  if (response?.is_success) {
    return { data: response.result.sales_agents || [], dataLength: response.result.sales_agents.length || 0 };
  }
  return { data: [], dataLength: 0 };
}

export async function fetchSalesTeamMemberTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, setupId, teamId }: any) {
  const response = await getSalesTeamMemberTableData(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
    },
    setupId,
    teamId,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchProductGrpInsurerTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState, productGrpId }: any) {
  const response = await getProductGrpInsurer(productGrpId, {
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

export async function fetchProductGroupTeamTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState, productGrpId, currentInsurencerId }: any) {
  const response = await getProductGroupTeamTableData(productGrpId, currentInsurencerId, {
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
