import { getFilterString } from '@/components/others/FilterPopup';
import { getAllUserSalesTarget, getAllUser, getAllUserRoles, getAllUserYearSalesTarget, getAllTeam } from './api-service';

// export async function fetchTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, status: string) {
//   const response = await getAllUser({
//     search: searchValue.toLowerCase(),
//     page: currentPage,
//     limit: itemsPerPage,
//     sort_by: sortBy,
//     sort_dir: sortDir,
//     status: status,
//     // filters: getFilterString(tableState.filters)
//   });

// if (response.is_success) {
//   return { data: response.result.data || [], dataLength: response.result.total || 0 };
// }
// }

export async function getAllRoles(searchValue: any, currentPage: any) {
  const response = await getAllUserRoles({ search: searchValue, page: currentPage });
  return response.result.data || [];
}

export async function fetchUserTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await getAllUser(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: getFilterString(tableState.filters),
    },
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllAssigneesDropdownData(searchValue: any, currentPage: any) {
  const response = await getAllUserRoles({ search: searchValue, page: currentPage });
  return response.result.data || [];
}

export async function fetchUserSalesTargetTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState, id, year }: any) {
  const response = await getAllUserSalesTarget(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: tableState.filters,
      userId: id,
      year: year,
    },
    true,
  );
  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchUserYearSalesTargetTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState, id }: any) {
  const response = await getAllUserYearSalesTarget(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: tableState.filters,
      userId: id,
    },
    true,
  );
  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function getAllUserDrpdown(searchValue: any, currentPage: any, role?: string) {
  const response = await getAllUser({ search: searchValue, page: currentPage, role: role }, false);

  return response.result.data || [];
}

export async function fetchAllTeamsDropdown(searchValue: any, currentPage: any) {
  const response = await getAllTeam({ search: searchValue, page: currentPage });

  return response.result.data || [];
}
