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
  customer_id?: string;
};

export async function getAllApprovals(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/quotation-approval?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function CreateNotes(formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/issued-policy-notes`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getOneNote(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/issued-policy-notes/${id}`,
      method: 'GET',
    }),
  );
}

export async function updateNote(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/issued-policy-notes/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function CreateEndorsementRequests(formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/endorsement-requests`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function createInvoicePayment(formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/payments`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getAllIssuedPolicies(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/issued-policy?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllNotes(params: GAParams, policyId: string, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/issued-policy/${policyId}/notes?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOneIssuedPolicy(id: any, abortDuplicate: boolean = false) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/issued-policy/${id}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function updateIssuedPolicy(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/issued-policy/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function getAllEndorsementDetails(id: any, params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/issued-policy/${id}/endorsement-details?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllInvoice(params: GAParams, abortDuplicate: boolean = false, policyId: string) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/issued-policy/${policyId}/invoices?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOnePolicyInvoice(id: any, abortDuplicate: boolean = false) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/invoices/${id}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllEndorsementRequests(id: any, params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/issued-policy/${id}/endorsement-requests?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllPayment(params: GAParams, abortDuplicate: boolean = false, policyId: string) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/issued-policy/${policyId}/payments?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllEndorsementTypes(params: GAParams, abortDuplicate: boolean = true) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/endorsement-types?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllReasonCodes(params: GAParams, id: any, abortDuplicate: boolean = true) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/endorsement-types/${id}/reason-codes?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function acceptEndorsementRequest(formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/endorsement-details`,
    method: 'POST',
    data: formData,
  });

  return responseHandling(response);
}

export async function getAllIssuedPolicyDocuments(params: GAParams, id: string, type: string, abortDuplicate: boolean = true) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/issued-policy/${id}/documents/${type}?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllIssuedPolicyInheritanceHistory(params: GAParams, id: string, abortDuplicate: boolean = true) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/issued-policy/${id}/issued-policy-renewal?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOneIssuedPolicyDocument(id: string, abortDuplicate: boolean = true) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/issued-policy/documents/${id}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function createIssuedPolicyDocuments(formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/issued-policy/documents/bulk-create`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function deleteIssuedPolicyDocument(id: string) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/issued-policy/documents/${id}`,
    method: 'DELETE',
  });

  return responseHandling(response);
}

export async function sendEndorsementEmail(formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/send-endorsement-request`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function uploadConfirmationReceipt(formData: any, id: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/payments/${id}`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function getIssuedPolicyDocuments(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/policy-base/${id}/product-documents`,
      method: 'GET',
    }),
  );
}

export async function getAllChatMsg(params: GAParams, abortDuplicate: boolean, endorsement_id: string) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.POLICY_PROXY_PREFIX}/api/policy-endorsement/${endorsement_id}/chat?${queryString}`,
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

export async function getSyncChatMsg(abortDuplicate: boolean, policy_id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/policy/${policy_id}/sync-endorsement-requests`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function updateIssuedPolicyDocument(id: string, formData: any) {
  const response = await sendRequest({
    url: `${process.env.POLICY_PROXY_PREFIX}/api/policy-base/${id}/product-documents`,
    method: 'PUT',
    data: formData,
  });
  return responseHandling(response);
}

export async function getEndorsementRequestDocuments(id: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CORE_PROXY_PREFIX}/api/endorsement/${id}/documents`,
      method: 'GET',
    }),
  );
}
