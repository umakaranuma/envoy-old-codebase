import { getAllPartnerContact, getAllPartnerProduct, getAllPartnerRQuotation, getAllPartners } from './api-service';

export async function fetchPartnerTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await getAllPartners(
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

export async function fetchPartnerContactTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState, sp_id }: any) {
  const response = await getAllPartnerContact(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: tableState.filters,
    },
    true,
    sp_id,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchPartnerRQuotationTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState, sp_id }: any) {
  const response = await getAllPartnerRQuotation(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: tableState.filters,
    },
    true,
    sp_id,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchPartnerProductTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState, sp_id }: any) {
  const response = await getAllPartnerProduct(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: tableState.filters,
    },
    true,
    sp_id,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}
