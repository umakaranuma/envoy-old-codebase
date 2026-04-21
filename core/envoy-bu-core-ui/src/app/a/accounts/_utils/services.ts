import { useTrans } from '@/helpers/services/lang/langService';
import { getAllAccTapData, getAllCustomerContact, getAllCustomers } from './api-service';
import { getAllContacts } from '../../contacts/_utils/api-service';
import { getFilterString } from '@/components/others/FilterPopup';

export const customerTypes = () => {
  const t = useTrans('label.accounts');
  return [
    { label: t('corporate'), value: 'Corporate' },
    { label: t('personal'), value: 'Personal' },
  ];
};

export async function fetchCustomerTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await getAllCustomers(
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

export async function fetchCustomerContactTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState, id }: any) {
  const response = await getAllCustomerContact(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: tableState.filters,
    },
    true,
    id,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchContacts(searchValue: any, currentPage: any) {
  const response = await getAllContacts({ search: searchValue, page: currentPage }, false);

  return response.result.data || [];
}

export async function fetchAllCustomers(searchValue: any, currentPage: any, id?: any) {
  const response = await getAllCustomers({ search: searchValue, page: currentPage, ignore: id }, false);

  return response.result.data || [];
}

export async function fetchAccTapTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState, id, tap }: any) {
  const response = await getAllAccTapData(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: tableState.filters,
    },
    true,
    id,
    tap,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}
