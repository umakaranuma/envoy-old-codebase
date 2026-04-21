import {
  getAgentCommissionPayments,
  getAllCommissionHistory,
  getAllSingleAgentCommison,
  getAllUsers,
  getBrokerageRevenuesPayments,
  getMultiAgentRevenuesPayments,
  getMultiBrokerageRevenuesPayments,
  getMyCommissionPayments,
  getOneCommissionHistoryCalculated,
  getOneCommissionHistoryDeductible,
} from './api-service';

export async function fetchBrokerageRevenuesTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState = {}, start_date = '', end_date = '', insurer_id = '' }: any) {
  const filters = tableState && tableState.filters && Object.keys(tableState.filters).length > 0 ? { filters: JSON.stringify(tableState.filters) } : {};

  const response = await getBrokerageRevenuesPayments(
    {
      search: searchValue?.toLowerCase?.() || '',
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      ...filters,
      insurer_id,
      start_date,
      end_date,
    },
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchMultiAgentRevenuesTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, start_date = '', end_date = '', data, status }: any) {
  const response = await getMultiAgentRevenuesPayments(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      start_date: start_date,
      end_date: end_date,
      status: status,
    },
    false,
    data,
  );

  if (response.is_success) {
    return { data: response?.result?.data || [], dataLength: response?.result?.total_records || 0 };
  }
}
export async function fetchMultiBrokerageRevenuesTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, start_date = '', end_date = '', data, negative_outstanding }: any) {
  const response = await getMultiBrokerageRevenuesPayments(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      start_date: start_date,
      end_date: end_date,
      negative_outstanding,
    },
    false,
    data,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAgentCommissionTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await getAgentCommissionPayments(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      // ...(Object.keys(tableState.filters).length > 0 && { filters: JSON.stringify(tableState.filters) }),
      filters: tableState,
    },
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchMyCommissionTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await getMyCommissionPayments(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      // ...(Object.keys(tableState.filters).length > 0 && { filters: JSON.stringify(tableState.filters) }),
      filters: tableState,
    },
    false,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchCommissionHistoryTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await getAllCommissionHistory(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      // ...(Object.keys(tableState.filters).length > 0 && { filters: JSON.stringify(tableState.filters) }),
      filters: tableState,
    },
    false,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllUsersData(searchValue: any, currentPage: any) {
  const response = await getAllUsers({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllSingleAgentCommisonTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, id }: any) {
  const response = await getAllSingleAgentCommison(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
    },
    id,
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchOneCommissionHistoryCalculatedData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, commissionId: string) {
  const response = await getOneCommissionHistoryCalculated(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
    },
    commissionId,
    false,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchOneCommissionHistoryDeductible({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, commissionId: string) {
  const response = await getOneCommissionHistoryDeductible(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
    },
    commissionId,
    false,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}
