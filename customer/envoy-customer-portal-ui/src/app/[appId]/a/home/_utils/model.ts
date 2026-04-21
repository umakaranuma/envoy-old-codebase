export const initFormData = {
  name: '',
  description: '',
  injuryStatus: '',
  admittedStatus: '',
  settlementType: '',
  contact_number: '',
  customer_id: '',
  is_myself: true,
  policy_id: '',
  form_id: '',
  reporter_name: '',
  reporter_relationship: '',
  reporter_contact: '',
  risk_info_ids: [],
};

export interface IPolicyInfo {
  form_id: number;
  policy_holder_info: PolicyHolderInfo;
  policy_info: PolicyInfo;
  request_info: RequestInfo;
  insurer_info: InsurerInfo;
  risk_info: RiskInfo;
  product_info: ProductInfo;
  user_info: UserInfo;
}

export interface PolicyHolderInfo {
  customer_id: number;
  customer_name: string;
  customer_logo: string;
  customer_contact_name: string;
  customer_contact_email: string;
  customer_contact_primary: string;
  customer_contact_address: string;
  customer_title: string;
}

export interface PolicyInfo {
  policy_id: number;
  brokerage_policy_id: string;
  insurer_policy_id: any;
  insurer_invoice_id: string;
  start_date: string;
  end_date: string;
  premium_amount: string;
  sum_insured: string;
  quotation_document: string;
  quotation_document_name: string;
}

export interface RequestInfo {
  request_type_id: number;
  request_type_name: string;
  coverage_type_id: number;
  coverage_type_name: string;
  payment_plan_id: number;
  payment_plan_name: string;
}

export interface InsurerInfo {
  insurer_id: number;
  insurer_name: string;
  insurer_logo: any;
  insurer_mail: string;
  insurer_description: any;
  insurer_contact_number: any;
}

export interface RiskInfo {
  risk_type_id: number;
  risk_type_title: string;
}

export interface ProductInfo {
  product_id: number;
  product_name: string;
}

export interface UserInfo {
  requested_by_id: number;
  requested_by_name: string;
  requested_by_logo: any;
  created_by_id: number;
  created_by_name: string;
  created_by_logo: any;
  updated_by_id: any;
  updated_by_name: any;
  updated_by_logo: any;
}
