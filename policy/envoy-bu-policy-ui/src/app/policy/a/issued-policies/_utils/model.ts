export const initPolicy = {
  code: '',
};

export const initFormData = {
  name: '',
  description: '',
  endorsement_type: null,
  request_policy_id: '',
};

export interface IIssuedPolicies {
  name?: string;
  description?: string;
  color?: string;
}
export interface INotes {
  id?: string;
  is_high_priority?: number;
  notes: string;
}

export interface IPolicy {
  name?: string;
  description?: string;
  color?: string;
}

export const notesFormData = {
  title: '',
  content: '',
  health: '',
  added_by: '',
  issued_policy_id: '',
  updated_by: '',
  date: '',
  remarks: '',
};
export interface IIssuedPolicy {
  id: number;
  brokerage_policy_id: string;
  start_date: string;
  end_date: string;
  paid_amount: null;
  credit_period_days: number;
  credit_age_days: number;
  insurer_invoice_id: string;
  insurer_policy_id: string;
  sum_insured: string;
  premium_amount: string;
  policy_effective_date: string;
  policy_document: null;
  policy_document_name: null;
  remarks: null;
  invoice_document: null;
  invoice_document_name: null;
  initial_premium_amount: null;
  is_renewal: null;
  account_manager_id: null;
  entity_id: number;
  sales_agent_id: null;
  policy_base_id: number;
  policy_request_id: number;
  policy_id: number;
  insurer_notes: null;
  product_id: number;
  risk_type_name: string;
  risk_type_id: number;
  insurer_info_full_name: string;
  insurer_id: number;
  insurer_info_logo: string;
  customer_name: string;
  customer_logo: string;
  customer_id: number;
  product: string;
  policy_request_code: string;
  policy_request_status: string;
  policy_request_status_color: string;
  quotation_document: null;
  quotation_document_name: null;
  requested_by: string;
  requested_by_logo: null;
  request_type: string;
  request_type_id: number;
  customer_email: null;
  customer_address: null;
  customer_primary_contact: string;
  coverage_type: string;
  coverage_type_id: number;
  payment_plan: string;
  payment_plan_id: number;
  created_by: string;
  created_by_logo: null;
  updated_by: null;
  updated_by_logo: null;
  created_at: string;
  updated_at: string;
  invoice_number: string;
  settled_amount: string;
  pending_amount: string;
  status_name: string;
  status_color: string;
  status_id: number;
  credit_age: number;
  policy_request: PolicyRequest;
  risk_types: RiskType[];
  status: Status;
  policy_request_date: string;
  sales_agent_name: string;
  account_manager: string;
  status_type: string;
}

interface PolicyRequest {
  id: number;
  policy_request_id: string;
  policy_request_date: Date;
  entity_id: number;
  policy_base_id: number;
  status_id: number;
  email_data: string;
}

interface RiskType {
  risk_type_id: number;
  risk_type_name: string;
  risk_type_description: string;
}

interface Status {
  id: number;
  name: string;
  color: string;
}
export const initEndorsementCreate = {
  remarks: '',
  endorsement_type_id: null,
  reason_code_id: '',
  cover_value: '',
  issued_policy_id: '',
};

export interface IEndorsement {
  endorsement_type_id: string;
  reason_code_id: string;
  cover_value: string;
  issued_policy_id: string;
  endorsement_request: string;
  entity_id: string;
  mail_status: string;
  id: string;
}

export const invoicePaymentFormData = {
  created_at: '',
  created_by: '',
  paid_amount: '',
  invoice_id: '',
  invoice_amount: '',
  outstanding_amount: '',
  upload_receipt: '',
  remarks: '',
  created_by_name: '',
  total_amount: '',
  new_outstanding_amount: '',
  reference_id: '',
};

export interface IEmailData {
  id: string;
  endorsement_request: string;
  requested_amount: null;
  cover_value: string;
  entity_id: string;
  endorsement_type_id: string;
  issued_policy_id: string;
  reason_code_id: string;
  mail_status: string;
  endorsement_type_name: string;
  reason_code: string;
  reason_code_description: string;
  remarks: null;
  created_by: string;
  created_by_logo: null;
  created_at: Date;
  insurer_name: string;
  insurer_logo: null;
  insurer_id: string;
  insurer_email: null;
  effective_date: string;
  policy_id: string;
  policy_holder_name: string;
  policy_holder_logo: string;
  policy_holder_email: string;
  policy_holder_address: string;
  policy_holder_primary_contact: string;
}

export interface IPolicyDocuments {
  id: number;
  name: string;
  is_mandatory: number;
  vendor_product_id: number;
  type: string;
  value: Value;
}

interface Value {
  doc: string;
  type: string;
  name: string;
}
