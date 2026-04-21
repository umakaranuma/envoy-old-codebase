export interface IPaymentFormData {
  paid_amount: string;
  endorsement_type_id: string;
  invoice_amount: string;
  outstanding_amount: string;
  payment_method: string;
  file: File | null;
  reference_id: string;
  invoice_number: string;
  previous_outstanding_amount?: string;
}

export const initPolicyHolderInfo = {
  policy_holder_name: '',
  date_of_birth: '',
  gender: '',
  nic: '',
  phone_number: '',
  email: '',
  contact_method: '',
  address: '',
  is_myself: false,
};

export interface ISupportingDocument {
  id: number;
  name: string;
  is_mandatory: number;
  vendor_product_id: number;
  type: 'policy' | 'risk';
}

export interface IDocument {
  document_type_id: number;
  name: string;
  is_mandatory: boolean;
  type: string;
  value: any;
  uploaded_at: any;
}

export interface IMultiDocuments {
  file: File | null;
  error: boolean;
  baseName: string;
  extension: string;
  notes: string;
}

export interface IResource {
  [key: string]: {
    doc: string;
    name: string;
    type: string;
  };
}

export interface ITermsAndConditions {
  vendor_product_name: string;
  documents: ITermDocument[];
}

export interface ITermDocument {
  id: number;
  entity_id: number;
  doc: string;
  name: string;
  type: string;
}

export interface IReviewInfo {
  request_id: number;
  request_code: string;
  type: string;
  status: string;
  vendor_product_ids: number[];
  risk_type_ids: number[];
  form_submission_id: number;
  form_values: FormValue[];
  documents: Document[];
  coverages: Coverages;
  policy_holder: PolicyHolder;
  payment_details: PaymentDetails;
}

export interface Coverages {
  sum_insured: string;
  start_date: Date;
  end_date: Date;
  is_draft: boolean;
  created_at: Date;
}

export interface Document {
  document_type_id: number;
  document_type__name: string;
  value: null | string;
  uploaded_at: Date;
}

export interface PaymentDetails {
  payment_method: string;
  payment_frequency: string;
  bank_number: string;
  account_holder_name: string;
  branch: string;
  bank_name: string;
  iban_swift_code: string;
  estimated_amount: string;
  is_draft: boolean;
  created_at: Date;
}

export interface FormValue {
  custom_form_element_id: number;
  form_element_id: number;
  value: null | string;
  label: null | string;
}

export interface PolicyHolder {
  id: number;
  policy_holder_name: string;
  date_of_birth: Date;
  gender: string;
  nic: string;
  phone_number: string;
  email: string;
  address: string;
  contact_method: string;
  is_draft: boolean;
}

export interface IPolicy {
  id: number;
  brokerage_policy_id: string;
  start_date: Date;
  end_date: Date;
  credit_period_days: number;
  credit_age_days: number;
  insurer_invoice_id: string;
  insurer_policy_id: null;
  sum_insured: string;
  premium_amount: string;
  policy_effective_date: Date;
  policy_document: null;
  policy_document_name: null;
  remarks: null;
  invoice_document: null;
  invoice_document_name: null;
  entity_id: number;
  policy_base_id: number;
  policy_request_id: null;
  initial_premium_amount: null;
  paid_amount: string;
  account_manager_id: null;
  sales_agent_id: number;
  is_renewal: number;
  insurer_notes: null;
  product_id: number;
  risk_type_name: string;
  risk_type_id: number;
  insurer_info_full_name: string;
  insurer_id: number;
  insurer_info_logo: null;
  customer_name: string;
  customer_logo: string;
  customer_id: number;
  product: string;
  policy_request_code: null;
  policy_request_status: string;
  policy_request_status_color: string;
  quotation_document: null;
  quotation_document_name: null;
  requested_by: null;
  requested_by_logo: null;
  request_type: string;
  request_type_id: number;
  customer_email: string;
  customer_address: string;
  customer_primary_contact: string;
  coverage_type: string;
  coverage_type_id: number;
  payment_plan: string;
  payment_plan_id: number;
  created_by: string;
  created_by_logo: null;
  updated_by: null;
  updated_by_logo: null;
  created_at: Date;
  updated_at: Date;
  invoice_number: string;
  outstanding_amount: string;
  endorsement_count: number;
}

export interface IPaymentDetails {
  payment_gateway_url: string;
  bank_details: BankDetails;
  service_provider: ServiceProvider;
}

export interface BankDetails {
  id: number;
  account_holder_name: string;
  bank_name: string;
  bank_branch: string;
  account_number: string;
  iban_swift_code: string;
  created_at: Date;
  updated_at: Date;
  user_id: number;
  payment_gateway_url: string;
  service_provider_id: number;
}

export interface ServiceProvider {
  id: number;
  name: string;
  email: string;
}
