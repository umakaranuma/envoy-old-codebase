import { getFilterString } from '@/components/others/FilterPopup';
import {
  getAllChannels,
  getAllContacts,
  getAllCurrencies,
  getAllCustomers,
  getOpportunityStages,
  getAllOpportunityTypes,
  getAllSalesAgents,
  getAllOpportunities,
  getAllOpportunityCollectedInfo,
  getAllNotesOfOpportunity,
  getAllInterestedProducts,
  getAllProducts,
  getAllOpInteractions,
  getAllAcountManger,
  getAllFlagType,
  getAllReasons,
} from './api-service';

export async function fetchOpportunityTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await getAllOpportunities(
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

export async function fetchTaskTableData() {
  return {
    data: [
      {
        id: '1',
        name: 'Lead #366',
        assigned_date: 'Company',
        due_date: 'Olivia Rhye',
        status: 'Biffco Enterprises Ltd.',
        assigned_to: '28/10/2012',
      },
      {
        id: '2',
        name: 'Lead #366',
        assigned_date: 'Company',
        due_date: 'Olivia Rhye',
        status: 'Biffco Enterprises Ltd.',
        assigned_to: '28/10/2012',
      },
      {
        id: '3',
        name: 'Lead #366',
        assigned_date: 'Company',
        due_date: 'Olivia Rhye',
        status: 'Biffco Enterprises Ltd.',
        assigned_to: '28/10/2012',
      },
      {
        id: '4',
        name: 'Lead #366',
        assigned_date: 'Company',
        due_date: 'Olivia Rhye',
        status: 'Biffco Enterprises Ltd.',
        assigned_to: '28/10/2012',
      },
    ],
    dataLength: 120,
  };
}

export async function fetchAllOpportunityStages(searchValue: any, currentPage: any, ignore: string = '') {
  const response = await getOpportunityStages({ search: searchValue, page: currentPage, ignore });

  return response.result || [];
}

export async function fetchAllOpportunities(searchValue: any, currentPage: any) {
  const response = await getAllOpportunities({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllChannel(searchValue: any, currentPage: any) {
  const response = await getAllChannels({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllOpportunityTypes(searchValue: any, currentPage: any, opportunityId: string = '') {
  const response = await getAllOpportunityTypes({ search: searchValue, page: currentPage, opportunityId: opportunityId });

  return response.result.data || [];
}

export async function fetchAllSalesAgents(searchValue: any, currentPage: any) {
  const response = await getAllSalesAgents({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllCurrency(searchValue: any, currentPage: any) {
  const response = await getAllCurrencies({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllCustomers(searchValue: any, currentPage: any) {
  const response = await getAllCustomers({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllContacts(searchValue: any, currentPage: any) {
  const response = await getAllContacts({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchOpportunityCollectInfoTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, opportunityId: string, formConfigId: string) {
  if (formConfigId) {
    const response = await getAllOpportunityCollectedInfo(
      {
        search: searchValue.toLowerCase(),
        page: currentPage,
        limit: itemsPerPage,
        sort_by: sortBy,
        sort_dir: sortDir,
      },
      opportunityId,
      formConfigId,
    );

    if (response.is_success) {
      return { data: response.result || [], dataLength: Array.isArray(response.result) ? response.result.length || 0 : 0 };
    }
  }
}

export async function fetchAllProductTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any, opId: any) {
  const response = await getAllInterestedProducts(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: tableState.filters,
    },
    opId,
    false,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllProducts(searchValue: any, currentPage: any) {
  const response = await getAllProducts({ search: searchValue, page: currentPage }, true);

  if (response.is_success) {
    return response.result.data || [];
  }
}

export async function fetchAllOpInteractionTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any, opId: any) {
  const response = await getAllOpInteractions(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: tableState.filters,
    },
    opId,
    false,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchNotesOpportunityTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any, id: any) {
  const response = await getAllNotesOfOpportunity(
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
    return { data: response.result || [], dataLength: Array.isArray(response.result) ? response.result.length || 0 : 0 };
  }
}

export async function fetchAllAcountManger(searchValue: any, currentPage: any) {
  const response = await getAllAcountManger({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllFlagType(searchValue: any, currentPage: any, entityId: string) {
  const response = await getAllFlagType({ search: searchValue, page: currentPage }, entityId, true);

  if (response.is_success) {
    return response.result.data || [];
  }
}

export async function fetchAllReasons(searchValue: any, currentPage: any) {
  const response = await getAllReasons({ search: searchValue, page: currentPage }, true);

  if (response.is_success) {
    return response.result.data || [];
  }
}
