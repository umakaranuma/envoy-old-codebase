import { getAllBillingInfo } from './api-service';

export async function fetchPaymentListTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any) {
  const response = await getAllBillingInfo({
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
