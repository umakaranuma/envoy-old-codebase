import { getAllChartsOfReport, getAllReports, getAllReportTypes, getOneReportData } from './api-service';

export async function fetchAllReportsTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any) {
  const response = await getAllReports({
    search: searchValue.toLowerCase(),
    page: currentPage,
    limit: itemsPerPage,
    sort_by: sortBy,
    sort_dir: sortDir,
  });

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllReportTypes(searchValue: any, currentPage: any) {
  const response = await getAllReportTypes({ search: searchValue, page: currentPage });
  return response.result.data || [];
}

export async function fetchOneReportTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, reportId: any) {
  const response = await getOneReportData(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
    },
    reportId,
  );

  if (response.is_success) {
    return { data: response.result.data.data || [], dataLength: response.result.total || 0 };
  }
}

export async function fetchAllReportFields(searchValue: any, currentPage: any, id: any) {
  const response = await getOneReportData({ search: searchValue, page: currentPage }, id);
  return response.result.data.json.fields || [];
}

export async function fetchOneReportChartTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, reportId: any) {
  const response = await getAllChartsOfReport(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
    },
    reportId,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export const CHART_TYPES = [
  { id: 'Single Bar', value: 'single-bar', axes: { x: 'single', y: 'single' } },
  { id: 'Stack Bar', value: 'stacked-bar', axes: { x: 'single', y: 'multiple' } },
  { id: 'Group Bar', value: 'group-bar', axes: { x: 'multiple', y: 'multiple' } },
  { id: 'Line (Single)', value: 'single-line', axes: { x: 'single', y: 'single' } },
  { id: 'Line (Multiple)', value: 'multi-line', axes: { x: 'single', y: 'multiple' } },
  { id: 'Donut Pie', value: 'donut-pie', axes: { x: 'single', y: 'single' } },
  { id: 'Scatterplot', value: 'scatter-plot', axes: { x: 'single', y: 'single' } },
  { id: 'Area Chart (Single)', value: 'single-area', axes: { x: 'single', y: 'single' } },
  { id: 'Area Chart (Multi)', value: 'multi-area', axes: { x: 'single', y: 'multiple' } },
];
