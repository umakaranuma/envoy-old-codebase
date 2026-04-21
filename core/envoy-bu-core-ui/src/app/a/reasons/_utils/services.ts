import { getFilterString } from '@/components/others/FilterPopup';
import { getAllEndorsementTypes, getAllReason } from './api-service';

export async function fetchReasonTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await getAllReason(
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

export const getReasonTypes = (t: any) => {
  return [
    { label: t('common'), value: 'Common' },
    { label: t('opportunity_flag'), value: 'Opportunity Flags' },
  ];
};

export async function fetchAllEndorsementTypes(searchValue: any, currentPage: any) {
  const response = await getAllEndorsementTypes({ search: searchValue, page: currentPage }, false);

  return response.result.data || [];
}
