import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { getAllTypesOfOpportunity } from '../../sales-management/_utils/api-service';
import {
  getAllAttributes,
  getAllContacts,
  getAllCustomers,
  getAllGeneratedDocumentList,
  getAllQuotations,
  getAllServiceProviders,
  getAllServiceProvidersOfQuotation,
  getAllServiceProvidersUsingProductId,
  getAllUsers,
  getAllVendorQuotation,
  getOpportunityInfo,
  quotationsForGenerateDocument,
} from './api-service';
import { local_storage } from '@/constans/StorageKeys';
import { getAllCoverages, getAllPaymentTypes, getAllProductsByType } from './policy-api-service';

export async function fetchQuotationTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any) {
  const response = await getAllQuotations(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      // filters: tableState.filters,
    },
    true,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllServiceProvidersOfQuotationTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, id: any) {
  const response = await getAllServiceProvidersOfQuotation(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      // filters: tableState.filters,
    },
    id,
  );

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export async function fetchAllServiceProviders(searchValue: any, currentPage: any) {
  const response = await getAllServiceProviders({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export async function fetchAllServiceProviderUsingProductId(category_ids?: string, lead_id?: string) {
  const response = await getAllServiceProvidersUsingProductId({ category_ids: category_ids, lead_id: lead_id, request_type: 'new' });

  return response.result || [];
}

export async function fetchAllServiceProvidersOfQuotation(searchValue: any, currentPage: any, id: any) {
  const response = await getAllServiceProvidersOfQuotation({ search: searchValue, page: currentPage }, id);

  return response.result.data || [];
}

// export async function fetchAllShortListedTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, id: any, selectedIds?: any) {
//   const response = await getAllShortlistedQuotation(
//     {
//       search: searchValue.toLowerCase(),
//       page: currentPage,
//       limit: itemsPerPage,
//       sort_by: sortBy,
//       sort_dir: sortDir,
//       selected_id: selectedIds || '',
//       // filters: tableState.filters,
//     },
//     id,
//     selectedIds,
//   );

//   if (response.is_success) {
//     return { data: response.result || [], dataLength: response.result.length || 0 };
//   }
// }

export async function fetchAllVendorQuotationTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, id: any, type: string) {
  const response = await getAllVendorQuotation(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filter: type,
    },
    id,
  );

  if (response.is_success) {
    return { data: response.result || [], dataLength: response.result.length || 0 };
  }
}

export async function fetchAllCriteria() {
  const response = await getAllAttributes();

  return response.result || [];
}

// export async function fetchDraftTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, id: any) {
//   const response = await getAllDraftQuotationList(
//     {
//       search: searchValue.toLowerCase(),
//       page: currentPage,
//       limit: itemsPerPage,
//       sort_by: sortBy,
//       sort_dir: sortDir,
//     },
//     id,
//   );

//   if (response.is_success) {
//     return { data: response.result || [], dataLength: response.result.length || 0 };
//   }
// }

export async function fetchGeneratedDocumentTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, id: any, status: string) {
  const response = await getAllGeneratedDocumentList(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      status: status,
    },
    id,
  );

  if (response.is_success) {
    return { data: response.result || [], dataLength: response.result.length || 0 };
  }
}

export async function fetchAllShortListDropdownData(searchValue: any, currentPage: any, id: any) {
  const response = await getAllVendorQuotation({ search: searchValue, page: currentPage, filter: 'shortlisted' }, id);
  if (response.is_success) {
    return response.result || [];
  }
}

export async function fetchAllGenerateDocumentListedTableData(id: any, selectedIds: any) {
  const response = await quotationsForGenerateDocument(id, selectedIds);

  if (response.is_success) {
    return { data: response.result || [], dataLength: response.result.length || 0 };
  }
}

export async function fetchAllCustomers(searchValue: any, currentPage: any) {
  const response = await getAllCustomers({ search: searchValue, page: currentPage }, false);

  return response.result.data || [];
}

export async function fetchContacts(searchValue: any, currentPage: any) {
  const response = await getAllContacts({ search: searchValue, page: currentPage }, false);

  return response.result.data || [];
}

export async function fetchAllTypesOfOpportunity(id: any) {
  const response = await getAllTypesOfOpportunity(id);

  return response.result || [];
}

export async function fetchAllUsers(searchValue: any, currentPage: any) {
  const response = await getAllUsers({ search: searchValue, page: currentPage });

  return response.result.data || [];
}

export const getDefaultEmailTemplateForInsurer = () => {
  const user = getLocalStorage(local_storage.auth_user_info);
  return ` <div className="container mt-5 p-4 bg-white border rounded shadow-sm text-dark" style={{ maxWidth: "700px" }}>
  <p>Dear Sir/Madam,</p>
<br />
  <p>
    I hope this message finds you well.
  </p>
<br />
  <p>Please find attached the quotation and the associated risk information for your review</p>
<br />
  <p>
   Please find attached the quotation for your company, Doe Enterprises, along with the associated risk information document. The quotation provides comprehensive insurance coverage tailored to meet your specific needs, ensuring protection for your commercial property against risks such as fire, theft, and natural disasters.
Thank you for considering ABC Insurance Company. We are committed to providing you with the best possible coverage and service.
  </p>
<br />
  <p>I look forward to your feedback.</p>
<br />
  <div className="mt-4">
    <p>Best Regards,</p>
    <p>${user.display_name ? user.display_name : ''}</p>
    <p>Email: ${user.email ? user.email : ''}</p>
  </div>
</div>`;
};

export const getDefaultEmailTemplateForCustomer = (customerName: string) => {
  const user = getLocalStorage(local_storage.auth_user_info);
  return ` <div className="container mt-5 p-4 bg-white border rounded shadow-sm text-dark" style={{ maxWidth: "700px" }}>
  <p>Dear ${customerName},</p>
<br />
  <p>
  Thank you for considering our services for your auto insurance needs. Based on the quotations received, we have prepared a recommendation document for the Car Safe Drive - Premium product.
  </p>
<br />
  <p>Attached: Recommendation Document</p>
<br />
 <p>
 Additionally, you can enroll in the selected policy through our customer portal using the link below:
  </p>
  <br />
  <p>
   <a href="#">Proceed to Enrolment</a>
  <p>
 Please review the document and feel free to reach out if you have any questions.
  </p>
<br />
  <p>Thank you for your trust in us!</p>
<br />
  <div className="mt-4">
    <p>Best Regards,</p>
    <p>${user.display_name ?? user.display_name}</p>
    <p>Email: ${user.email ?? user.email}</p>
  </div>
</div>`;
};

export const getPDFhtml = (content: string, selectedSP: { id: string; code: string }[], version: string, notes: string) => {
  const styledContent = `
  <style>
    .pdf-table thead {
      background-color: #f9f9f9 !important;
    }
    .pdf-table th {
      background-color: #f9f9f9 !important;
    }
  </style>
  <div class="pdf-table">
    ${content}
  </div>
`;

  return `<html>
  <head>
    <meta charset="UTF-8" />
    <title>PDF</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        font-size: 15px;
        color: #333333;
      }
      .heading {
        font-size: 15px;
        font-weight: bold;
        margin-bottom: 10px;
        padding-top: 5px;
      }
      table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 10px;
      }

      th, td {
       border-bottom: 1px solid #ddd;
        padding: 6px;
        text-align: left;
      }
      .label-table td {
       border: 1px 1px;
        padding-bottom: 2px;
        padding-top: 7px;
      }
      .comment-box {
        border: 1px solid #ccc;
        padding: 10px;
        min-height: 80px;
        background-color: #f9f9f9;
      }
      .header{
           background-color: #f9f9f9;
           text-align:center;
      }
    </style>
  </head>
  <body>
    <div class="heading">Key Data Points from Quotations</div>
    <table class="label-table">
      <tr class="header"><td><b>Field</b></td><td><b>Value</b></td></tr>
      <tr><td>Version</td><td>${version}</td></tr>
      <tr><td>Date</td><td>${new Date().toLocaleDateString('en-SL')}</td></tr>
      <tr><td>Created By</td><td>${getLocalStorage(local_storage.auth_user_info).display_name}</td></tr>
      <tr><td>Selected Quotations</td><td>${selectedSP.map((sp) => sp.code).join(' | ')}</td></tr>
    </table>

    <div class="heading">Consolidated Recommendation Document</div>
   ${styledContent}
    <div class="heading">Recommendation Comments</div>
    <div class="comment-box">${notes ? notes : '-'}</div>
  </body>
</html>
`;
};

export async function fetchAllProductsByType(searchValue?: any, currentPage?: any, typeIds?: number[], service_provider_id?: string, product_id?: string) {
  const response = await getAllProductsByType({ search: searchValue, page: currentPage, risk_type_id: typeIds, service_provider_id: service_provider_id, product_id: product_id }, false);
  return response.result || [];
}

export async function fetchAllCoverages(searchValue: any, currentPage: any) {
  const response = await getAllCoverages({ search: searchValue, page: currentPage }, false);
  return response.result.data || [];
}

export async function fetchAllPaymentTypes(searchValue: any, currentPage: any) {
  const response = await getAllPaymentTypes({ search: searchValue, page: currentPage }, false);
  return response.result.data || [];
}

export const getDefaultPolicyRequestEmailTemplateForInsurer = (serviceProviders: string, policyNumber: string) => {
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
    <ul>
      <li>Policy Number: ${policyNumber || '-'}</li>
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

export async function fetchOneRiskTypeTableData({ currentPage, itemsPerPage, sortBy, sortDir }: any, riskTypeId: string, customerId: string, leadId?: string) {
  const response = await getOpportunityInfo(
    {
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      customer_id: customerId,
      lead_id: leadId,
    },
    riskTypeId,
  );

  if (response.is_success) {
    return { data: response.result || [], dataLength: Array.isArray(response.result) ? response.result.length || 0 : 0 };
  }
}
