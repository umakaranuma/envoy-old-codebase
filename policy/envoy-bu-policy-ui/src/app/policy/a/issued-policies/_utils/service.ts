import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import {
  getAllEndorsementDetails,
  getAllEndorsementRequests,
  getAllEndorsementTypes,
  getAllInvoice,
  getAllIssuedPolicies,
  getAllIssuedPolicyDocuments,
  getAllIssuedPolicyInheritanceHistory,
  getAllPayment,
  getAllReasonCodes,
} from './api-service';
import { local_storage } from '@/constans/StorageKeys';
import { getAllNotesOfOpportunity } from '@/components/others/common/lead/api-service';

export async function fetchInvoiceTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any, policyId: any) {
  const response = await getAllInvoice(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: tableState.filters,
    },
    true,
    policyId,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchNotesTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any, entityId: any) {
  const response = await getAllNotesOfOpportunity(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: tableState.filters,
    },
    entityId,
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchPaymentTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir, tableState }: any, policyId: any) {
  const response = await getAllPayment(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filters: tableState.filters,
    },
    true,
    policyId,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchIssuedPoliciesTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any) {
  const response = await getAllIssuedPolicies({
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

export async function fetchEndorsementTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, id: any) {
  const response = await getAllEndorsementDetails(id, {
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

export async function fetchEndorsementRequestTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, id: any) {
  const response = await getAllEndorsementRequests(id, {
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

export async function fetchAllEndorsementTypes(searchValue: any, currentPage: any) {
  const response = await getAllEndorsementTypes({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllReasonCodes(searchValue: any, currentPage: any, id: any) {
  const response = await getAllReasonCodes({ search: searchValue, page: currentPage }, id);

  return response.result.data || [];
}

export async function fetchAllIssuedPolicies(searchValue: any, currentPage: any, customerId: string) {
  const response = await getAllIssuedPolicies({ search: searchValue, page: currentPage, customer_id: customerId });

  return response.result.data || [];
}

export async function fetchAllIssuedPolicyDocumentTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, policyId: any, type: any) {
  const response = await getAllIssuedPolicyDocuments(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
    },
    policyId,
    type,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchPolicyInheritanceTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, policyId: any) {
  const response = await getAllIssuedPolicyInheritanceHistory(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
    },
    policyId,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export const getDefaultEmailTemplateForInsurer = (serviceProviders: string, policyholderName: string, policyNumber: string, effectiveDate: string) => {
  const user = getLocalStorage(local_storage.auth_user_info);
  return `
  <div style="font-family: Arial, sans-serif; color: #333; max-width: 700px; margin: auto;">
    <p>Dear ${serviceProviders || ''},</p>
    <br/>
    <p>I hope this email finds you well.</p>
<br/>
    <p>
      I am writing to request an endorsement on the policy <strong>${policyNumber || '-'}</strong> under <strong>${policyholderName || '-'}</strong>. 
      Please find the details of the requested changes below:
    </p>
<br/>
    <ul>
      <li>Policyholder's Name: ${policyholderName || '-'}</li>
      <li>Policy Number: ${policyNumber || '-'}</li>
      <li>Effective Date of Endorsement: ${effectiveDate || '-'}</li>
    </ul>
    <br/>
    <p>We appreciate your prompt attention to this matter and look forward to your confirmation.</p>
    <p>Thank you for your continued support.</p>
    <br/>
    <p>Best regards,</p>
    <p>${user.display_name || '[Your Full Name]'}</p>
    <p>${user.email || '[Contact Information]'}</p>
  </div>
  `;
};

// <p><strong>Endorsement Requested Changes:</strong></p>
// <ol>
//   <li>
//     <strong>Increase in Coverage Limits:</strong>
//     <ul>
//       <li>Increase property damage coverage limit from [$100,000] to [$150,000].</li>
//     </ul>
//   </li>
// </ol>

// <p>
//   Please review the changes and provide a revised policy document or confirmation of the endorsement at your earliest convenience.
//   If there are any additional documents or information required, kindly let me know.
// </p>

// <p>${user.position || '[Your Position]'}</p>
// <p>${user.company_name || '[Your Company Name]'}</p>
