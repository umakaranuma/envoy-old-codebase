import { form } from '@/constans/Form';
import { responseHandling } from '@/helpers/handlers/responseHandler';
import { clearError } from '@/helpers/handlers/validationErrorHandler';
import sendRequest from 'apptimus-netlink';

type params = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string };

export async function getAllTypes(params: params) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getOneType(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types/${id}`,
      method: 'GET',
    }),
  );
}

export async function createtype(formData: any) {
  clearError(form.type_crud.store);
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function updateType(id: string, formData: any) {
  clearError(form.type_crud.update);

  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function deleteType(id: string) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types/${id}`,
    method: 'DELETE',
  });
  return responseHandling(response);
}

export async function FormsTableData(params: params, id: string) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types/${id}/forms?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function createTypesOfForm(id: any, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types/${id}/forms`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getOneForm(formId: string, id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types/${formId}/forms/${id}`,
      method: 'GET',
    }),
  );
}

export async function updateTypeForm(formId: string, id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types/${formId}/forms/${id}`,
    method: 'PUT',
    data: formData,
  });

  return responseHandling(response);
}

export async function deleteTypeForm(formId: string, id: string) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types/${id}/forms/${formId}`,
    method: 'DELETE',
  });
  return responseHandling(response);
}

export async function getAllOpportunityTypes(params: params) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/opportunity-types?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function getAllForms(params: params) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/templates?${queryString}`,
      method: 'GET',
    }),
  );
}
