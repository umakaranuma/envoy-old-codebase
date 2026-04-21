import { useTrans } from '@/helpers/services/lang/langService';
import { getAllContactGroups, getAllContacts, getAllContactsOfGroup, getAllInteractions, getAllMergeableContacts, getAvailableContacts, getMergeAccounts } from './api-service';

export const salutations = () => {
  const t = useTrans('label.contacts');
  return [
    { label: t('mr'), value: 'Mr.' },
    { label: t('mrs'), value: 'Mrs.' },
    { label: t('miss'), value: 'Miss' },
    { label: t('rev'), value: 'Rev.' },
  ];
};

export async function fetchContactTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await getAllContacts(
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

export async function fetchContactGroupTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await getAllContactGroups(
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

export async function fetchContactInteractionTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState, id }: any) {
  const response = await getAllInteractions(
    id,
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

  if (response.is_success && response.result) {
    // Map the data to match table column names
    const mappedData = response.result.map((item: any) => {
      return {
        ...item,
        interaction_type: item.channel_name, // Map channel_name to interaction_type
      };
    });
    console.log('Mapped data for table:', mappedData);
    return { data: mappedData || [], dataLength: mappedData.length || 0 };
  }
  return { data: [], dataLength: 0 };
}

export async function fetchAvailableContacts({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, groupId: any) {
  const response = await getAvailableContacts(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
    },
    true,
    groupId,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllContactsOfGroup({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, groupId: any) {
  const response = await getAllContactsOfGroup(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
    },
    groupId,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchMergeableContacts({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, ids: any) {
  const response = await getAllMergeableContacts(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
    },
    false,
    ids,
  );

  return { data: response.result || [], dataLength: response.result.length || 0 };
}

export async function fetchMergeableAccounts({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, id }: any) {
  const response = await getMergeAccounts(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
    },
    false,
    id,
  );
  const res = response.result.map((item: any) => item.core_customers);
  return { data: res || [], dataLength: response.result.length || 0 };
}
