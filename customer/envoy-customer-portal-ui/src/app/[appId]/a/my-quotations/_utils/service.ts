import { getAllQuotations, getAllQuotationServiceProviders } from './api-service';

export async function fetchAllQuotationsTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any) {
  const response = await getAllQuotations({
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

export async function fetchAllQuotationsSPTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any, id: any) {
  const response = await getAllQuotationServiceProviders(
    {
      search: searchValue.toLowerCase(),
      page: currentPage,
      limit: itemsPerPage,
      sort_by: sortBy,
      sort_dir: sortDir,
      filter: 'shortlisted',
    },
    id,
  );

  if (response.is_success) {
    return { data: response.result || [], dataLength: response.result.length || 0 };
  }
}

export async function fetchAllQuotationSPTableData() {
  return {
    data: [
      {
        id: 1,
        insurance_company_name: 'Allionz General Insurance',
        quotation_version: '21',
        quotation_request_number: 'QR001',
        received_date: '8-07-2024',
        quotation_value: 'LKR 150,000.00',
        updated_by: 'Olivia Rhye',
        quotation_link: 'View Details.pdf',
        quotation_request_link: 'www.example.com/qr001',
      },
      {
        id: 2,
        insurance_company_name: 'Ceylínco General Insurance',
        quotation_version: '2.0',
        quotation_request_number: 'QR002',
        received_date: '5-07-2024',
        quotation_value: 'LKR 167,000.00',
        updated_by: 'Jane Smith',
        quotation_link: 'View Details.pdf',
        quotation_request_link: 'www.example.com/qr002',
      },
      {
        id: 3,
        insurance_company_name: 'Fair first insurance',
        quotation_version: '1.0',
        quotation_request_number: 'QR003',
        received_date: '10-07-2024',
        quotation_value: 'LKR 90,000.00',
        updated_by: 'Jane Smith',
        quotation_link: 'View Details.pdf',
        quotation_request_link: 'www.example.com/qr003',
      },
    ],
    dataLength: 3,
  };
}

export async function fetchAllQuotationTableData() {
  return {
    data: [
      {
        id: 1,
        product_type: 'Auto insurance',
        quotation_id: 'R-1001',
        expiration_date: '20/10/2024',
        status: 'Reviewed',
        document: 'Recommendation.pdf',
      },
      { id: 2, product_type: 'Home insurance', quotation_id: 'R-1002', expiration_date: '15/11/2024', status: 'Pending', document: 'Proposal_Home.pdf' },
      { id: 3, product_type: 'Travel insurance', quotation_id: 'R-1003', expiration_date: '30/09/2024', status: 'Approved', document: 'Travel_Cover.pdf' },
      {
        id: 4,
        product_type: 'Health insurance',
        quotation_id: 'R-1004',
        expiration_date: '10/12/2024',
        status: 'Rejected',
        document: 'Health_Plan.pdf',
      },
      { id: 5, product_type: 'Life insurance', quotation_id: 'R-1005', expiration_date: '05/01/2025', status: 'Under Review', document: 'Life_Policy.pdf' },
    ],
    dataLength: 5,
  };
}
