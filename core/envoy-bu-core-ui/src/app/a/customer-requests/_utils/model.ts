export interface ICustomerRequest {
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
