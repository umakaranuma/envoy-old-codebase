import { responseHandling } from '@/helpers/handlers/responseHandler';
import sendRequest from 'apptimus-netlink';

type GAParams = { search?: string; page?: string; limit?: string; sort_by?: string; sort_dir?: string; filters?: string; status?: string; type?: string };

export async function getAllTemplates(params: GAParams, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/templates?${queryString}`,
      method: 'GET',
      abortDuplicate,
    }),
  );
}

export async function createTemplate(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/templates`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function createStep(formData: any, templateId: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/forms/${templateId}/steps`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function deleteStep(id: string, step_id: number) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/forms/${id}/steps/${step_id}`,
    method: 'DELETE',
  });
  return responseHandling(response);
}

export async function UpdateStep(formData: any, id: string, step_id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/forms/${id}/steps/${step_id}`,
    method: 'PATCH',
    data: formData,
  });
  return responseHandling(response);
}

export async function createPanel(formData: any, templateId: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/forms/${templateId}/panels`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function UpdatePanel(formData: any, id: string, panel_id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/forms/${id}/panels/${panel_id}`,
    method: 'PATCH',
    data: formData,
  });
  return responseHandling(response);
}

export async function duplicatePanel(templateId: string, panel_id: number) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/forms/${templateId}/panels/${panel_id}/duplicate`,
    method: 'POST',
  });
  return responseHandling(response);
}
export async function deletePanel(templateId: string, pannelId: number) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/forms/${templateId}/panels/${pannelId}`,
    method: 'DELETE',
  });
  return responseHandling(response);
}

export async function createElement(formData: any, templateId: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/forms/${templateId}/elements`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function deleteElement(templateId: string, elementId: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/forms/${templateId}/elements/${elementId}`,
    method: 'DELETE',
  });
  return responseHandling(response);
}

export async function updateElement(templateId: string, elementId: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/forms/${templateId}/elements/${elementId}`,
    method: 'PATCH',
    data: formData,
  });

  return responseHandling(response);
}

export async function updatetemplate(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/templates/${id}`,
    method: 'PUT',
    data: formData,
  });

  return responseHandling(response);
}

export async function deleteTemplate(id: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/templates/${id}`,
    method: 'DELETE',
  });
  return responseHandling(response);
}

export async function getAllTemplateFormElements(params: GAParams, abortDuplicate: boolean) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/templates/form-elements?${queryString}`,
      method: 'GET',
      abortDuplicate,
    }),
  );
}

export async function getOneTemplate(templateId: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/templates/${templateId}`,
      method: 'GET',
    }),
  );
}

export async function updateTemplate(formData: any, templateId: string) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/templates/${templateId}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function getTemplateSteps(templateId: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/forms/${templateId}/steps`,
      method: 'GET',
    }),
  );
}
