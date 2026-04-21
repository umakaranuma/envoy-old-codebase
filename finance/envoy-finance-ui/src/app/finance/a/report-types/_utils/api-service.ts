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

export async function getAllReportTypes(params: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.REPORTS_PROXY_PREFIX}/api/report-types?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function deleteReportType(id: string) {
  const response = await sendRequest({
    url: `${process.env.REPORTS_PROXY_PREFIX}/api/report-types/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function createReportType(formData: any) {
  const response = await sendRequest({
    url: `${process.env.REPORTS_PROXY_PREFIX}/api/report-types`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getOneReportType(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.REPORTS_PROXY_PREFIX}/api/report-types/${id}`,
      method: 'GET',
    }),
  );
}

export async function updateReportType(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.REPORTS_PROXY_PREFIX}/api/report-types/${id}`,
    method: 'PUT',
    data: formData,
  });

  return responseHandling(response);
}
