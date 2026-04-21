import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type GAParams = {
  search?: string;
  page?: string;
  limit?: string;
  sort_by?: string;
  sort_dir?: string;
  filters?: string;
  status?: string;
  type?: string;
  stage_id?: string;
  sales_agent_id?: string;
  ids?: string;
  opportunityId?: string;
  ignore?: string;
  fields?: string;
};

export async function getAllReports(params: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.REPORTS_PROXY_PREFIX}/api/reports?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getAllReportTypes(params: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.REPORTS_PROXY_PREFIX}/api/report-types?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function deleteReport(id: string) {
  const response = await sendRequest({
    url: `${process.env.REPORTS_PROXY_PREFIX}/api/reports/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function updateReport(formData: any, id: string) {
  const response = await sendRequest({
    url: `${process.env.REPORTS_PROXY_PREFIX}/api/reports/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function createReport(formData: any) {
  const response = await sendRequest({
    url: `${process.env.REPORTS_PROXY_PREFIX}/api/reports`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getOneReport(reportId: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.REPORTS_PROXY_PREFIX}/api/reports/${reportId}`,
      method: 'GET',
    }),
  );
}

export async function getOneReportData(params: GAParams, reportId: string) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.REPORTS_PROXY_PREFIX}/api/report-data/${reportId}?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function createReportChart(formData: any) {
  const response = await sendRequest({
    url: `${process.env.REPORTS_PROXY_PREFIX}/api/report-charts`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getAllChartsOfReport(params: GAParams, reportId: string) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.REPORTS_PROXY_PREFIX}/api/report-charts/report/${reportId}?${queryString}`,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
}

export async function deleteChartOfReport(id: string) {
  const response = await sendRequest({
    url: `${process.env.REPORTS_PROXY_PREFIX}/api/report-charts/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function getOneChartOfReport(id: string, abortDuplicate: boolean = true) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.REPORTS_PROXY_PREFIX}/api/report-charts/${id}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function updateReportChart(formData: any, id: string) {
  const response = await sendRequest({
    url: `${process.env.REPORTS_PROXY_PREFIX}/api/report-charts/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

// export async function getExcelReportUrl(formData: any) {
//   const response = await sendRequest({
//     url: `${process.env.REPORTS_PROXY_PREFIX}/api/report/doc-export`,
//     method: 'POST',
//     data: formData,
//   });
//   return responseHandling(response);
// }

export async function getExportedReportUrl(formData: any) {
  const response = await sendRequest({
    url: `${process.env.REPORTS_PROXY_PREFIX}/api/report/html_to_doc_export`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}
