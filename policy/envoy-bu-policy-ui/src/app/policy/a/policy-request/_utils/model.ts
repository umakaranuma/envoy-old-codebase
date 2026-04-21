export interface IUpdatePolicyInfo {
  name?: string;
  description?: string;
  color?: string;
}

export const initFormData = {
  form_id: '',
  data_gethering_type: 'ONBOARDING',
  opportunity_type_id: '',
  title: '',
  description: '',
  name: '',
};

export interface IType {
  id: string;
  title: string;
  description: string;
}

export interface IForm {
  title: string;
  type: string;
  description?: string;
}

export const initPolicyData = {
  name: '',
  description: '',
  customer_id: '',
  lead_id: '',
  customer_primary_contact: '',
  customer_email: '',
  customer_address: '',
  quotation_document_name: '',
  quotation_document: '',
  premium_amount: '',
  quotation_issued_date: '',
  quotation_expiry_date: '',
  quotation_notes: '',
  risk_type_id: '',
  risk_type_ids: [],
  product_id: '',
  payment_mode_id: '',
  sum_insured: '',
  coverage_type_id: '',
  policy_start_date: '',
  policy_expiry_date: '',
  insurer_id: '',
  request_by_id: '',
  request_by_name: '',
  insurer_notes: '',
  request_type_id: '',
  start_date: null,
  end_date: '',
  credit_period_days: '',
  credit_age_days: null,
  insurer_invoice_id: '',
  policy_effective_date: '',
  policy_document: '',
  policy_document_name: '',
  insurer_policy_id: '',
  customer_name: '',
  product_name: '',
  coverage_type_name: '',
  payment_mode_name: '',
  risks: [] as any[],
  is_policy: false,
  insurer_name: '',
  is_renewal: 0,
  sales_agent_id: '',
  sales_agent_name: '',
  policy_id: '',
  risk_ids: [] as number[],
  invoice_document_name: '',
  quotation_code: '',
  coverage_details: '',
  coverage_details_name: '',
  quotation_id: '',
  group_id: '',
  defaultRisk: [] as any[],
  product_type: '',
  product_documents: [] as any[],
  brokerage_policy_number: '',
  issued_policy_id: '',
  issued_policy_premium_amount: '',
  issued_policy_sum_insured: '',
  policy_draft_documents: [] as any[],
  risk_draft_documents: [] as any[],
  account_manager_name: '',
  account_manager_id: '',
};

export interface IOpportunityType {
  name?: string;
  title: string;
  description?: string;
}

export interface IPolicy {
  name?: string;
  description?: string;
  color?: string;
}

export interface DocumentValue {
  id: number;
  value: string;
  document_name: string;
}

export const initIssuedFormData = {
  brokerage_policy_id: '',
  start_date: '',
  end_date: '',
  premium_amount: '',
  credit_period_days: '',
  credit_age_days: '',
  insurer_invoice_id: '',
  sum_insured: '',
  policy_effective_date: '',
  policy_document: '',
  policy_document_size: '',
  policy_document_name: '',
  policy_request_id: '',
};

export const initUpdatePolicyRequestFormData = {
  policy_start_date: '',
  policy_expiry_date: '',
  premium_amount: '',
  credit_period_days: '',
  credit_age_days: '',
  insurer_invoice_id: '',
  sum_insured: '',
  policy_effective_date: '',
  policy_document: '',
  policy_document_name: '',
  insurer_policy_id: '',
};

export interface IMultiDocuments {
  file: File | null;
  error: boolean;
  baseName: string;
  extension: string;
  notes: string;
}

export interface IElements {
  id: number;
  label: string;
  element_id: number;
  element_code: string;
  step_id: number | null;
  panel_id: number;
  parent_id: number;
  code: string;
  category: string;
  order_number: number;
  column_size: number;
  is_required: number;
  options: any[];
  value: any | null;
}

export interface IExcelMappingResponse {
  success: boolean;
  message: string;
  result: {
    headers: Array<{ key: number; value: string | number }>;
    rows: Array<Record<string, string>>;
  };
  system_code: number;
}

export interface IProductDocument {
  id: number;
  name: string;
  is_mandatory: number;
  vendor_product_id: number;
  type: string;
}

export interface IDocument {
  [key: string]: {
    doc: string;
    name: string;
    type: string;
  };
}

export interface IRequestPolicy {
  id: number;
  policy_request_id: string;
  policy_request_date: Date;
  entity_id: number;
  policy_base_id: number;
  status_id: number;
  email_data: string;
  premium_amount: null;
  sum_insured: string;
  quotation_issued_date: null;
  quotation_expiry_date: null;
  policy_start_date: string;
  policy_expiry_date: string;
  quotation_notes: string;
  quotation_document_name: null;
  quotation_document: null;
  insurer_company_name: string;
  insurer_company_logo: string;
  risk_type: string;
  requested_by: string;
  requested_by_logo: null;
  status: string;
  status_color: string;
  request_type: string;
  products: Product[];
  customer_name: string;
  customer_email: string;
  customer_primary_contact: string;
  customer_address: string;
  insurer_notes: null;
  coverage_type: string;
  payment_plan: string;
  created_at: Date;
  created_by: string;
  created_by_logo: null;
  updated_by: null;
  updated_by_logo: null;
  issued_policy_id: number;
  brokerage_policy_id: string;
  issued_start_date: Date;
  issued_end_date: Date;
  issued_paid_amount: string;
  credit_period_days: number;
  credit_age_days: number;
  insurer_policy_id: string;
  insurer_invoice_id: string;
  issued_sum_insured: string;
  issued_premium_amount: string;
  policy_effective_date: null;
  policy_document: null;
  policy_document_name: null;
  invoice_document: null;
  invoice_document_name: null;
  initial_premium_amount: null;
  issued_remarks: null;
  is_renewal: null;
  issued_policy_request_id: number;
  issued_entity_id: number;
  issued_policy_base_id: number;
  customer_title: string;
  policy_document_value: DocumentValue[];
  risk_document_value: DocumentValue[];
  risk_types: RiskType[];
  sales_agent_name: string;
  account_manager_name: string;
  customer_id: string;
  quotation_code: string;
  confirmed_vendor_responses: ConfirmedVendorResponse[];
}

export interface ConfirmedVendorResponse {
  id: number;
  quotation_id: number;
  quotation_document: string;
  quotation_document_name: string;
  quotation_document_type: string;
  quotation_issued_date: Date;
  service_provider_name: string;
  service_provider_logo: string;
  quotation_code: string;
  quotation_expiry_date: Date;
}
interface Product {
  id: number;
  name: string;
  is_primary: number;
}

interface RiskType {
  risk_type_id: number;
  risk_type_name: string;
  risk_type_description: string;
}

export interface IExtractResult {
  policy_details: IPolicyDetails;
  invoice_details: IInvoiceDetails;
}

export interface IPolicyDetails {
  document_name: string;
  insurer_policy_id: string;
  policy_issue_date: string;
  start_date: string;
  end_date: string;
  credit_period_days: string;
  credit_age_days?: string;
  sum_insured: string;
  risk_type: string;
  payment_mode: string;
  requested_by: string;
  sales_agent: string;
  policy_document_url: string;
  policy_document_name: string;
  policy_document_type: string;
}

export interface IInvoiceDetails {
  document_name: string;
  insurer_invoice_id: string;
  insurer_invoice_number: string;
  amount_or_cover_value: string;
  invoice_document_url: string;
  invoice_document_name: string;
  invoice_document_type: string;
}

export const initIssuedPolicyFormData = {
  insurer_policy_id: '',
  insurer_invoice_id: '',
  policy_effective_date: '',
  policy_start_date: '',
  policy_expiry_date: '',
  premium_amount: null,
  credit_period_days: '',
  invoice_document_name: '',
  invoice_document: '',
  policy_document: '',
  policy_document_name: '',
};

export interface INewCustomerInfo {
  name: string;
  id: string;
  email: string;
  primary_contact: string;
}
