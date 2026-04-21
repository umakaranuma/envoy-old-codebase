import { getAllNotification } from './api-service';

export async function fetchAllNotificationTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, read_status: string, filter: string) {
  const response = await getAllNotification({
    search: searchValue.toLowerCase(),
    page: currentPage,
    limit: itemsPerPage,
    sort_by: sortBy,
    sort_dir: sortDir,
    read_status,
    filter,
  });

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}
