import { getAllIncentiveData } from './api-service';

export async function fetchAllIncentiveData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any) {
  const response = await getAllIncentiveData(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
    },
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}
