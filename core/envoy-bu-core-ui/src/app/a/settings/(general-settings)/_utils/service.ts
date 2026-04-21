import { getAllTaskConfigs, getAllTaskTypes, getOpportunityStages } from './api-service';

type Value = string | string[];

export interface IFilterValue {
  o: string;
  v: Value;
  t: 'T' | 'A';
}

export interface IFilters {
  [key: string]: IFilterValue;
}

export const getFilterString = (filterData: IFilters) => {
  const formDataObject: IFilters = Object.fromEntries(Object.entries(filterData).filter(([fieldName, value]) => fieldName && value && value.v !== ''));

  return JSON.stringify(formDataObject);
};

export async function fetchTaskConfigTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any) {
  const response = await getAllTaskConfigs(
    {
      search: searchValue,
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

export async function fetchAllOpportunityStages(searchValue: any, currentPage: any, ignore: string = '') {
  const response = await getOpportunityStages({ search: searchValue, page: currentPage, ignore });

  return response.result || [];
}

export async function fetchAllTaskTypes(searchValue: any, currentPage: any) {
  const response = await getAllTaskTypes({ search: searchValue, page: currentPage });

  if (response.is_success) {
    return response.result.data || [];
  }
}
