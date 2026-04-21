import { getAllInvoicePayments, getAllInvoices, getAllInvoiceStatus, getAllPaymentStatus, getAllServiceRendered, getAllServiceRenderTypes } from './api-service';

export async function fetchServiceRenderedTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await getAllServiceRendered(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      ...(Object.keys(tableState.filters).length > 0 && { filters: JSON.stringify(tableState.filters) }),
    },
    false,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllPaymentStatus(searchValue: any, currentPage: any) {
  const response = await getAllPaymentStatus({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllInvoiceStatus(searchValue: any, currentPage: any) {
  const response = await getAllInvoiceStatus({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllInvoice(searchValue: any, currentPage: any) {
  const response = await getAllInvoices({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllServiceRenderTypes(searchValue: any, currentPage: any) {
  const response = await getAllServiceRenderTypes({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchPaymentTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, serviceRenderId: string) {
  if (!serviceRenderId) {
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
    serviceRenderId,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}
