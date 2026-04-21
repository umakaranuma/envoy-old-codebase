import { getAllCustomers } from '@/api-services/common';
import { getAllInvoicePayments, getAllInvoices, getAllUsers } from './api-service';

export async function fetchInvoiceTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any) {
  const response = await getAllInvoices(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      // ...(Object.keys(tableState.filters).length > 0 && { filters: JSON.stringify(tableState.filters) }),
    },
    false,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchPaymentTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, invoiceId: string) {
  if (!invoiceId) {
    throw new Error('Invoice ID is required to fetch payments');
  }

  const response = await getAllInvoicePayments(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      // ...(Object.keys(tableState.filters).length > 0 && { filters: JSON.stringify(tableState.filters) }),
    },
    invoiceId,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllUsers(searchValue: any, currentPage: any) {
  const response = await getAllUsers({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllCustomers(searchValue: any, currentPage: any) {
  const response = await getAllCustomers({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchErrorTableData() {
  // { searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any
  // const response = await getAllInvoices(
  //   {
  //     search: searchValue.toLowerCase(),
  //     page: currentPage,
  //     limit: itemsPerPage,
  //     sort_by: sortBy,
  //     sort_dir: sortDir,
  //     filters: tableState.filters,
  //   },
  //   true,
  // );

  // if (response.is_success) {
  //   return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  // }
  return {
    data: [
      { record_number: '001', error_description: 'Description Details here' },
      { record_number: '002', error_description: 'Another error description here' },
    ],
    dataLength: 2,
  };
}
