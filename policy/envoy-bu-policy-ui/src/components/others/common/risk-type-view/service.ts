import { getAllRiskInfoOfType } from './api-service';

export async function fetchOneRiskInfoTableData({ currentPage, itemsPerPage, sortBy, sortDir }: any, riskTypeId: string, customerId: string, policyBaseId?: string) {
  const response = await getAllRiskInfoOfType(
    {
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      customer_id: customerId,
      policy_base_id: policyBaseId,
    },
    riskTypeId,
  );

  if (response.is_success) {
    return { data: response.result || [], dataLength: Array.isArray(response.result) ? response.result.length || 0 : 0 };
  }
}
