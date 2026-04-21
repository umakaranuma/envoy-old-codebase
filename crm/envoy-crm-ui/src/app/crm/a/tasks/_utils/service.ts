import { getAllOpportunities, getAllTaskStatuses, getAllTaskTypes, getAllUsers } from '@/api-services/common';
import { getAllAssigneeHistories, getAllAssignees, getAllAssigneTask, getAllInteractionOfTask, getAllTaskSatuses, getAllTaskStatusesOfTask } from './api-service';
import { getFilterString } from '@/components/others/FilterPopup';

export async function fetchUserTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any) {
  const response = await getAllUsers(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
    },
    false,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllTaskTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any, opId: any) {
  const response = await getAllAssigneTask(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: getFilterString(tableState.filters),
      opportunity_id: opId ? opId : '',
    },
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllStatusTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await getAllTaskSatuses(
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
    return { data: response.result || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllAssignees({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await getAllAssignees(
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

export async function fetchAllTaskTypes(searchValue: any, currentPage: any) {
  const response = await getAllTaskTypes({ search: searchValue, page: currentPage });

  if (response.is_success) {
    return response.result.data || [];
  }
}

export async function fetchAllTaskStatuses(searchValue: any, currentPage: any) {
  const response = await getAllTaskStatuses({ search: searchValue, page: currentPage });

  if (response.is_success) {
    return response.result || [];
  }
}

export async function fetchAllOpportunities(searchValue: any, currentPage: any) {
  const response = await getAllOpportunities({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllAssigneesDropdownData(searchValue: any, currentPage: any) {
  const response = await getAllUsers({ search: searchValue, page: currentPage });

  if (response.is_success) {
    return response.result.data || [];
  }
}

export async function fetchAllAssigneeHistories({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any, id: any) {
  const response = await getAllAssigneeHistories(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: tableState.filters,
    },
    id,
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllStatusOfTaskTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any, id: any) {
  const response = await getAllTaskStatusesOfTask(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: tableState.filters,
    },
    id,
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllInteractionTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any, id: any) {
  const response = await getAllInteractionOfTask(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: tableState.filters,
    },
    id,
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}
