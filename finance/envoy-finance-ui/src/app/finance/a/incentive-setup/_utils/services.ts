import { getAllAsyncSelect, getAllIncentiveBaseField, getAllIncentiveSetupData, getAllRepeationType } from './api-service';

export async function fetchAllIncentiveSetupData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any) {
  const response = await getAllIncentiveSetupData(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
    },
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

// export async function fetchAllRewardTypeData(searchValue: any, currentPage: any) {
//   const response = await getAllRewardType({ search: searchValue, page: currentPage });

//   return response.result || [];
// }

export async function fetchAllRepeationTypeData(searchValue: any, currentPage: any) {
  const response = await getAllRepeationType({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllIncentiveBaseFieldData(searchValue: any, currentPage: any) {
  const response = await getAllIncentiveBaseField({ search: searchValue, page: currentPage });

  const fields = response.result.data || [];
  const definitions = response.result.definitions || {};

  return fields.map((item: string) => ({
    value: item,
    label: formatLabel(item),
    description: definitions[item]?.short_description || '',
  }));
}

function formatLabel(snakeCase: string): string {
  return snakeCase
    .split('_')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

export async function fetchAllAsyncSelectData(searchValue: any, currentPage: any, prefix: string, apiUrl: string) {
  const response = await getAllAsyncSelect({ search: searchValue, page: currentPage }, prefix, apiUrl);

  return response.result.data || [];
}
