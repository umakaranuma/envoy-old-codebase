import { getAllChannels } from './api-service';

export async function fetchChannelsTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await getAllChannels(
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
