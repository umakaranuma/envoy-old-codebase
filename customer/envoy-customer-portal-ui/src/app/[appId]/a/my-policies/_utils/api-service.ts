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
  risk_type_id?: string;
};

export async function createPolicyHolder(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/policy-holder`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getOnePolicyHolderInfo(requestId: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/policy-holder/${requestId}`,
      method: 'GET',
    }),
  );
}

export async function createPolicyFormTemplate(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/form-submission`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getMyselfInfo() {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/me`,
      method: 'GET',
    }),
  );
}

export async function getSupportingDocuments(params: GAParams, requestId: string) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/insurer-products/${requestId}/documents-enhanced?${queryString}`,
      method: 'GET',
    }),
  );
}

export async function createSupportingDocuments(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/request-documents`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function createCoverageInfo(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/request-coverage`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getOneCoverageInfo(requestId: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/request-coverage/${requestId}`,
      method: 'GET',
    }),
  );
}

export async function createPaymentInfo(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/request-payment-details`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getOnePaymentInfo(requestId: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/request-payment-details/${requestId}`,
      method: 'GET',
    }),
  );
}

export async function getTermsAndPolicyInfo(requestId: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/terms-conditions/${requestId}?type=product`,
      method: 'GET',
    }),
  );
}

export async function getReviewIInfo(requestId: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/request-details/${requestId}`,
      method: 'GET',
    }),
  );
}

export async function submitPolicyInfo(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/finalize-request/${formData.request_id}`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getAllPolicies(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/policies?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOnePolicy(policyId: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/policies/${policyId}`,
      method: 'GET',
    }),
  );
}

export async function getAllPolicyTransactions(params: GAParams, policyId: string, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/policy/${policyId}/policy-settlement?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllInterestedProducts(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/products-filters?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllRiskTypes(params: GAParams, abortDuplicate: boolean = false) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/opportunity-types?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getAllInvoices(params: GAParams, policyId: string, abortDuplicate: boolean = true) {
  const queryString = new URLSearchParams(params).toString();
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/policy/${policyId}/invoices?${queryString}`,
      method: 'GET',
      abortDuplicate: abortDuplicate,
    }),
  );
}

export async function getOnePolicyBankInfo(policyId: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/policy/${policyId}/bankinfo`,
      method: 'GET',
    }),
  );
}

export async function addSettlement(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/policy-settlement`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function createCommercialLineRequest(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/create_request`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function downloadTemplate(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/excel-exporter`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function uploadCommercialRiskInfoExcel(formData: any) {
  const response = await sendRequest({
    url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/risk-document`,
    method: 'POST',
    data: formData,
  });
  return responseHandling(response);
}

export async function getOneRiskInfoTemplate(requestId: string) {
  return responseHandling(
    await sendRequest({
      url: `${process.env.CUSTOMER_PROXY_PREFIX}/api/customer/risk-document/${requestId}`,
      method: 'GET',
    }),
  );
}
