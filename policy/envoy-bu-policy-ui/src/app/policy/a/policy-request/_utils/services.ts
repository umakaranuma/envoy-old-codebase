import { getAllCustomers } from '@/api-services/common';
import {
  FormsTableData,
  getAllCoverages,
  getAllForms,
  getAllInsurers,
  getAllOpportunities,
  getAllPaymentTypes,
  getAllPolicyRequests,
  getAllProductTypes,
  getAllUsers,
  getAllRiskInfoByRiskType,
  getAllProductsByType,
  getAccountManager,
  getAllSalesAgent,
} from './api-service';
import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';

export async function fetchPolicyRequestTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any) {
  const response = await getAllPolicyRequests({
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

export async function fetchAllFormsData(searchValue: any, currentPage: any) {
  const response = await getAllForms({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllTypeForms({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, typeId: any) {
  const response = await FormsTableData(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
    },
    typeId,
  );
  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllUsers(searchValue: any, currentPage: any) {
  const response = await getAllUsers({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllSalesAgent(searchValue: any, currentPage: any, managerId?: string, productId?: any, productGroupId?: any) {
  const response = await getAllSalesAgent({ search: searchValue, page: currentPage, manager_id: managerId, product_id: productId, product_group_id: productGroupId });

  return response.result.data || [];
}

export async function fetchAllCustomers(searchValue: any, currentPage: any) {
  const response = await getAllCustomers({ search: searchValue, page: currentPage }, false);

  return response.result.data || [];
}

export async function fetchAllProductTypes(searchValue: any, currentPage: any) {
  const response = await getAllProductTypes({ search: searchValue, page: currentPage }, false);
  return response.result.data || [];
}

export async function fetchAllCoverages(searchValue: any, currentPage: any) {
  const response = await getAllCoverages({ search: searchValue, page: currentPage }, false);
  return response.result.data || [];
}

export async function fetchAllPaymentTypes(searchValue: any, currentPage: any) {
  const response = await getAllPaymentTypes({ search: searchValue, page: currentPage }, false);
  return response.result.data || [];
}

export async function fetchAllInsurers(searchValue: any, currentPage: any, riskTypeIds: number[], groupId?: string, productId?: string) {
  const response = await getAllInsurers({ search: searchValue, page: currentPage, group_id: groupId, product_id: productId, risk_type_ids: riskTypeIds }, false);
  return response.result || [];
}

export async function fetchAllOpportunities(searchValue: any, currentPage: any, customerId: string) {
  const response = await getAllOpportunities({ search: searchValue, page: currentPage, fields: 'additional', stage: 'opportunity_qualified', customer_id: customerId }, false);
  return response.result.data || [];
}

export async function fetchOneRiskTypeTableData({ currentPage, itemsPerPage, sortBy, sortDir }: any, riskTypeId: string, customerId: string, leadId?: string | undefined, policyBaseId?: string) {
  const response = await getAllRiskInfoByRiskType(
    {
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      customer_id: customerId,
      lead_id: leadId,
      policy_base_id: policyBaseId,
    },
    riskTypeId,
  );

  if (response.is_success) {
    return { data: response.result || [], dataLength: Array.isArray(response.result) ? response.result.length || 0 : 0 };
  }
}

export async function fetchAllProductsByType(searchValue: any, currentPage: any, typeIds: number[]) {
  const response = await getAllProductsByType({ search: searchValue, page: currentPage, risk_type_id: typeIds }, false);
  return response.result || [];
}

export async function fetchAllAccountManagers(searchValue: any, currentPage: any, agentId?: string, productId?: any, productGroupId?: any) {
  const response = await getAccountManager({ search: searchValue, page: currentPage, agent_Id: agentId, product_id: productId, product_group_id: productGroupId });
  return response.result.data || [];
}

export const getDefaultPolicyRequestEmailTemplateForInsurer = (serviceProviders: string) => {
  const user = getLocalStorage(local_storage.auth_user_info);
  return `
  <div style="font-family: Arial, sans-serif; color: #333; max-width: 700px; margin: auto;">
    <p>Dear ${serviceProviders || ''},</p>
    <br/>
    <p>I hope this email finds you well.</p>
<br/>
    <p>
      We are writing to request your confirmation regarding the policy number mentioned below. Please review the details and confirm at your earliest convenience.
    </p>
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
// <ul>
//   <li>Policy Number: ${policyNumber || '-'}</li>
// </ul>
