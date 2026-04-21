import { getAllInvoices, getAllPayments } from './api-service';

export async function fetchAllPaymentData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any) {
  const response = await getAllPayments(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      // ...(Object.keys(tableState.filters).length > 0 && { filters: JSON.stringify(tableState.filters) })
    },
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllInvoiceData(searchValue: any, currentPage: any, type?: string) {
  const params: any = {
    page: currentPage,
  };

  if (searchValue) {
    params.search = searchValue;
  }

  if (type) {
    params.type = type;
  }

  const response = await getAllInvoices(params);

  return response.result.data || [];
}
