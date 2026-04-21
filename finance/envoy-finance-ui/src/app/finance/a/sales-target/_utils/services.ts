import { getAllAgent, getAllAgentSalesTarget, getAllSalesTeam, getAllTeamSalesTarget } from './api-service';

export async function fetchAllAgentSalesTarget({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any) {
  const response = await getAllAgentSalesTarget(
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

export async function fetchAllTeamSalesTarget({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any) {
  const response = await getAllTeamSalesTarget(
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

export async function fetchAllSalesTeamData(searchValue: any, currentPage: any) {
  const response = await getAllSalesTeam({ search: searchValue, page: currentPage });
  return response.result.data || [];
}

export async function fetchAllAgentTeamData(formdata: any) {
  const response = await getAllSalesTeam(formdata);
  return response.result.data || [];
}

export async function fetchAllAgentData(searchValue: any, currentPage: any, keywords: string[]) {
  const apiFormData = { keywords: keywords };
  const response = await getAllAgent({ search: searchValue, page: currentPage }, apiFormData);
  return response.result.data || [];
}
