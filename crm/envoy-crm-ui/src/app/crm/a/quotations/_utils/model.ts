export const initCustomerFormData = {
  type: '',
  code: '',
  name: '',
  remarks: '',
  parent_id: null as string | null,
  primary_contact_id_id: '',
  primary_contact: '',
};

export const initRequestCreateFormData = {
  lead_id: '',
  opportunity_type_id: [],
  request_type: '',
  notes: '',
  service_provider_id: [],
};

export const initRequestFormData = {
  id: 1,
  code: '',
  requested_data: '',
  customer_id: '',
  status: '',
  notes: '',
  request_type: '',
  created_by_name: '',
  opportunity_type_id: [],
  opportunity_id: '',
  opportunity_type: [],
};

export const initAddQuotation = {
  id: '',
  quotation_id: '',
  service_provider_id: '',
  by_user_id: '',
  coverage_details: '',
  code: '',
  quotation_value: '',
  review: '',
  version: '',
  received_date: '',
  expiry_date: '',
  total_amount: '',
  status: 'PENDING',
  re_request: '',
  quotation_request_link: '',
  service_provider_name: '',
  coverage_details_name: '',
  coverage_details_type: '',
  by_user_name: '',
  quotation_code: '',
  quotation_request_type: '',
  quotation_version: '',
  remaining_days: '',
};

export interface IReceivedQuotation {
  id: string;
  service_provider_id: string;
  service_provider_name: string;
  by_user_name: string;
  by_user_id: string;
  quotation_code: string;
  quotation_request_type: string;
  quotation_version: string;
  coverage_details: string;
  code: string;
  quotation_value: string;
  review: string;
  version: string;
  received_date: string;
  remaining_days: string;
  expiry_date: string;
  total_amount: string;
  status: string;
  re_request: string;
  quotation_request_link: string;
  coverage_details_name: string;
  coverage_details_type: string;
}

export const statusTypes = [
  { label: 'PENDING', value: 'PENDING' },
  { label: 'REJECTED', value: 'REJECTED' },
  { label: 'CONFIRMED', value: 'CONFIRMED' },
];

export const initGenerateForm = {
  vendor_quotation_ids: [],
  attribute_id: [],
  is_sent: false,
  is_draft: false,
  comment: '',
  version: '',
  customer_id: '',
  customer_name: '',
  send_quotation_id: '',
  documents: [],
  document_id: '',
  expiry_date: '',
};

export const initUploadDoc = {
  quotation_request_id: '',
  doc_link: '',
  doc_type: '',
  doc_name: '',
  uploaded_by: '',
  uploaded_date: '',
  version: '',
  uploaded_by_name: '',
};

export interface IAttribute {
  // id: number;
  title: string;
  // type: string;
  // form_id: number;
  column: string;
}

export const initContactFormData = {
  title: '',
  name: '',
  email: '',
  address: '',
  primary_contact: '',
  secondary_contact: '',
  remarks: '',
  picture: '',
  merged_contacts: [],
  contact_id: '',
};

export const initFormData = {
  id: '',
  type: '',
  code: '',
  name: '',
  remarks: '',
  parent_id: null as string | null,
  primary_contact: '',
  website_url: '',
  address: '',
  email: '',
  secondary_contact: '',
  contact_id: '',
  flex_fields: {} as Record<string, string>,
};

export interface ICompareData {
  vendor_quotation_id: string;
  service_provider_name: string;
  by_user_id: string;
  by_user_name: string;
  coverage_details_type: string;
  coverage_details_name: string;
  quotation_request_link: string;
  re_request: string;
  status: string;
  total_amount: string;
  expiry_date: string;
  received_date: string;
  version: string;
  review: string;
  quotation_value: string;
  code: string;
  coverage_details: string;
  document_extracted_details?: any;
}

export interface IDocument {
  send_quotation_id: string;
  version: string;
  uploaded_date: Date;
  uploaded_by: string;
  uploaded_by_name: string;
  opportunity_id: null;
  entity_id: string;
  status: string;
  quotation_request_id: string;
  form_submission_ids: string[];
  attribute_ids: string[];
  service_provider_ids: string[];
  vendor_quotation_ids: string[];
  values: Value[];
}

export interface Value {
  form_submission_id: string;
  attribute_id: string;
  value: string;
  service_provider_id: string;
}

export interface IEmailData {
  documents: document[];
  id: string;
  name: string;
  send_quotation_id: string;
}
interface document {
  doc: string;
  name: string;
}

export interface IEmailDocument {
  coverage_details: string;
  coverage_details_name: string;
}

export interface IProductDocument {
  id: number;
  name: string;
  is_mandatory: number;
  vendor_product_id: number;
  type: string;
}

export interface IIDocument {
  [key: string]: {
    doc: string;
    name: string;
    type: string;
  };
}

export const initPolicyRequestForm = {
  coverage_details_name: '',
  coverage_details: '',
  quotation_code: '',
  quotation_id: '',
  quotation_expiry_date: '',
  quotation_issued_date: '',
  premium_amount: '',

  coverage_type_id: '',
  coverage_type_name: '',
  is_renewal: 0,
  risk_type_ids: [] as number[],
  product_id: '',
  product_name: '',
  sum_insured: '',
  policy_start_date: '',
  policy_expiry_date: '',
  payment_mode_id: '',
  payment_mode_name: '',
  risk_ids: [] as number[],

  insurer_name: '',
  insurer_id: '',
  request_by_id: '',
  request_by_name: '',
  sales_agent_id: '',
  sales_agent_name: '',

  product_type: '',
  service_provider_id: '',
};

export interface IElement {
  id: number;
  label: string;
  step_id: number;
  form_id: number;
  order_number: number;
  panel_id: number;
  code: string;
  options?: any[];
  value?: any;
  column_size: any;
  is_required: any;
  category: string;
  parent_id: number;
}
