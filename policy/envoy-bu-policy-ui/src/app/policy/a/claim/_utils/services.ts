import { getAllClaims, getAllCustomersForClaims, getAllPoliciesOfCustomer } from './api-service';

export async function fetchClaimTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any, type: string) {
  const response = await getAllClaims(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: tableState.filters,
      status_type: type,
    },
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchPolicyInformationTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  return {
    data: [
      {
        id: '1',
        name: 'Test',
        description: 'Test description',
      },
      {
        id: '2',
        name: 'Test 2',
        description: 'Test description 2',
      },
      {
        id: '3',
        name: 'Test 3',
        description: 'Test description 3',
      },
      {
        id: '4',
        name: 'Test 4',
        description: 'Test description 4',
      },
      {
        id: '5',
        name: 'Test 5',
        description: 'Test description 5',
      },
      {
        id: '6',
        name: 'Test 6',
        description: 'Test description 6',
      },
      {
        id: '7',
        name: 'Test 7',
        description: 'Test description 7',
      },
    ],
    dataLength: 120,
  };

  const response = await getAllClaims(
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

export async function fetchAllCustomersForClaim(searchValue: any, currentPage: any) {
  const response = await getAllCustomersForClaims({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchPoliciesOfCustomer(searchValue: any, currentPage: any, customerId: any) {
  const response = await getAllPoliciesOfCustomer({ search: searchValue, page: currentPage }, customerId);

  return response.result.data || [];
}
