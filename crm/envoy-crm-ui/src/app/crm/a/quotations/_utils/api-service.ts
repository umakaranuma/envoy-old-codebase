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
  selected_id?: string;
  filter?: string;
  category_ids?: string;
  request_type?: string;
  lead_id?: string;
  customer_id?: string;
};

export async function getAllQuotations(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/quotations?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllServiceProviders(params: GAParams, abortDuplicate: boolean = true) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/service-providers?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllServiceProvidersUsingProductId(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/service-providers-type?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function createRequest(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/quotations`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getQuotationBasicInfo(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/quotations/${id}/basic-info`,
      method: 'GET',
    }),
  );
}

export async function getQuotationRiskInfoFile(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/quotations/${id}/risk-export`,
      method: 'GET',
    }),
  );
}

export async function getAllServiceProvidersOfQuotation(params: GAParams, id: any, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/quotations/${id}/service-providers?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getDocumentNextVersion(id: any, abortDuplicate: boolean = false) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/quotations/${id}/generate-doc-version`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllVendorQuotation(params: GAParams, id: any, abortDuplicate: boolean = true) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/quotations/${id}/vendor-responses?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllAttributes() {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/quotations/related-fields`,
      method: 'GET',
    }),
  );
}

export async function createReceivedDocument(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/quotations/vendor-responses`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function updateQuotation(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/quotations/vendor-responses/${id}`,
    method: 'PUT',
    data: formData,
  });

  return responseHandling(response);
}

export async function getOneReceivedQuotation(id: any) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/quotations/vendor-responses/${id}`,
      method: 'GET',
    }),
  );
}

export async function updateShortList(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/quotations/vendor-responses/${id}/shortlist`,
    method: 'PUT',
    data: formData,
  });

  return responseHandling(response);
}

// export async function getAllDraftQuotationList(params: GAParams, id: any, abortDuplicate: boolean = true) {
//   const queryString = new URLSearchParams(params).toString();
//   return responseHandling(
//     await sendRequest({
//       url: `${process.env.CRM_PROXY_PREFIX}/api/quotations/${id}/draft-forms?${queryString}`,
//       method: 'GET',
//       abortDuplicate: abortDuplicate,
//     }),
//   );
// }

export async function getAllGeneratedDocumentList(params: GAParams, id: any, abortDuplicate: boolean = true) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/quotations/${id}/generate-document?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function generateDocument(id: any, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/quotations/${id}/generate-document`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function quotationsForGenerateDocument(id: string, selectedIds: any) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/quotations/${id}/preview-data?selected_id=${selectedIds}`,
      method: 'GET',
    }),
  );
}

export async function getOneGeneratedDocument(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/generate-document/${id}`,
      method: 'GET',
    }),
  );
}

export async function getAllCustomers(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/customers?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllContacts(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/contacts?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function createCustomerContacts(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/customers/${id}/contacts`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function createContact(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/contacts`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function createCustomers(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/customers`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function createHierarchies(id: any, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/customers/${id}/hierarchies`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function sendApproval(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/send_approval`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function createPDF(id: any, formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/quotations/export-html-to-pdf/${id}`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function sendEmailToCustomer(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/quotations/send-email`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function uploadGeneratedDocument(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/generate-document/upload`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function deleteReceivedQuotation(id: string) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/quotations/vendor-responses/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function getAllUsers(params: GAParams) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/users?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function confirmReceivedQuotation(id: string) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/quotations/generate-document/${id}/confirm`,
    method: 'PUT',
  });

  return responseHandling(response);
}

export async function getAllChatMsg(params: GAParams, abortDuplicate: boolean, quotation_id: string, insurer_id: string) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/${quotation_id}/chat-messages/${insurer_id}?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function createMsg(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CORE_PROXY_PREFIX}/api/chatmail/send`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getOpportunityInfo(params: GAParams, riskTypeId: any) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/risk-values/${riskTypeId}?${queryString}`,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
}

export async function getPolicyRiskInfoFile(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/policy-base/${id}/export-risks`,
      method: 'GET',
    }),
  );
}

export async function getSyncChatMsg(abortDuplicate: boolean, quotation_id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/quotation/${quotation_id}/sync-conversations`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function revertQuotation(id: string) {
  const response = await sendRequest({
    url: `${process.env.CRM_PROXY_PREFIX}/api/quotations/${id}/revert`,
    method: 'POST',
  });
  return responseHandling(response);
}

export async function getDocumentData(documentId: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CRM_PROXY_PREFIX}/api/document-data-extract/${documentId}`,
      method: 'GET',
      abortDuplicate: true,
    }),
  );
}
