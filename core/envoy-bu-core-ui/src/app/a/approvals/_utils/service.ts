import { getAllApprovals, getOpportunityInfoOfApproval } from './api-service';

export async function fetchApprovalTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, status: string) {
  const response = await getAllApprovals({
    search: searchValue.toLowerCase(),
    page: currentPage,
    limit: itemsPerPage,
    sort_by: sortBy,
    sort_dir: sortDir,
    status: status,
  });

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchOneRiskTypeTableData({ currentPage, itemsPerPage, sortBy, sortDir }: any, riskTypeId: string, customerId: string, approvalId?: string) {
  const response = await getOpportunityInfoOfApproval(
    {
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      customer_id: customerId,
      approval_id: approvalId,
    },
    riskTypeId,
  );

  if (response.is_success) {
    return { data: response.result || [], dataLength: Array.isArray(response.result) ? response.result.length || 0 : 0 };
  }
}
