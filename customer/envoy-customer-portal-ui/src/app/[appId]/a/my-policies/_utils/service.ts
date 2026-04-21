import { getAllInterestedProducts, getAllInvoices, getAllPolicies, getAllPolicyTransactions, getAllRiskTypes } from './api-service';

export async function fetchPoliciesTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any) {
  const response = await getAllPolicies({
    search: searchValue.toLowerCase(),
    page: currentPage,
    limit: itemsPerPage,
    sort_by: sortBy,
    sort_dir: sortDir,
  });

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllPolicyTransactionTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, policyId: string) {
  const response = await getAllPolicyTransactions(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
    },
    policyId,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllInterestedProducts(searchValue: any, currentPage: any, riskTypeId: string) {
  const response = await getAllInterestedProducts({ search: searchValue, page: currentPage, risk_type_id: riskTypeId });

  return response.result || [];
}

export async function fetchAllRiskTypes(searchValue: any, currentPage: any) {
  const response = await getAllRiskTypes({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllInvoices(searchValue: any, currentPage: any, policyId: string) {
  const response = await getAllInvoices({ search: searchValue, page: currentPage }, policyId);

  return response.result.data || [];
}
