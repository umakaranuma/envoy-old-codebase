import { getAllCustomers } from '@/api-services/common';
import { getAllLeadsByCustomer, getAllRisks, getAllRisksByLead, getAllRisksByPolicyBase, getAllRisksHistories } from './api-service';

export async function fetchRiskTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await getAllRisks(
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
export async function fetchAllCustomers(searchValue: any, currentPage: any) {
  const response = await getAllCustomers({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllLeadsByCustomer(searchValue: any, currentPage: any, customerId: string) {
  const response = await getAllLeadsByCustomer({ search: searchValue, page: currentPage }, customerId);

  return response.result.data || [];
}

export async function fetchAllRiskTypesByLead(searchValue: any, currentPage: any, leadId: string) {
  const response = await getAllRisksByLead({ search: searchValue, page: currentPage, lead_id: leadId });

  return response.result.data || [];
}

export async function fetchAllRiskTypesByPolicyBase(searchValue: any, currentPage: any, policyBaseId: string) {
  const response = await getAllRisksByPolicyBase({ search: searchValue, page: currentPage }, policyBaseId);

  return response.result || [];
}

export async function fetchRiskHistoryTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, riskId: string) {
  const response = await getAllRisksHistories(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
    },
    riskId,
    true,
  );

  if (response.is_success) {
    return { data: response.result || [], dataLength: response.result.length || 0 };
  }
}
