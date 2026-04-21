import { FormsTableData, getAllForms, getAllTypes } from './api-service';

export async function fetchAllTypes({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any) {
  const response = await getAllTypes({
    search: searchValue.toLowerCase(),
    page: currentPage,
    limit: itemsPerPage,
    sort_by: sortBy,
    sort_dir: sortDir,
  });

  return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
}

export async function fetchAllTypeForms({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, typeId: any) {
  const response = await FormsTableData(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
    },
    typeId,
  );

  return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
}

export async function fetchAllFormsData(searchValue: any, currentPage: any) {
  const response = await getAllForms({ search: searchValue, page: currentPage });

  return response.result.data || [];
}
