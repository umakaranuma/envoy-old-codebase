import { getAllReportTypes } from './api-service';

export async function fetchAllReportTypesTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any) {
  const response = await getAllReportTypes({
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

export const MODULES = [
  { label: 'CRM', value: 'CRM' },
  { label: 'POLICY', value: 'POLICY' },
  { label: 'FINANCE', value: 'FINANCE' },
  { label: 'CORE', value: 'CORE' },
];
