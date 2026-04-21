import { getAllNativeProducts } from '../../products/_utils/api-service';
import { getAllTeams } from './api-service';

export async function fetchAllNativeProducts(searchValue: any, currentPage: any) {
  const response = await getAllNativeProducts({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchTeamTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await getAllTeams(
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
