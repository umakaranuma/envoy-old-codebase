export const initFormData = {
  name: '',
  description: '',
};

export interface IInvoice {
  invoice_no?: string;
  invoice_date?: string;
  insurer_policy_no?: string;
  invoice_pay_type?: string;
}

export interface InvoiceDetails {
  invoice_number: string;
  invoice_type: string;
  invoice_date: string;
  insurer_policy_no: string;
  payment_type: string;
  policy_start_date: string;
  policy_end_date: string;
  policy_number: string;
  transaction_type: string;
  invoice_amount: string;
  paid_amount: string;
  outstanding_amount: string;
  due_date: string;
  payment_status: string;
  insured_name: string;
  insured_contact: string;
  insured_email: string;
  insured_address: string;
  insurer_name: string;
  insurer_contact: string;
  insurer_email: string;
  insurer_address: string;
  product_name: string;
  product_code: string;
  product_type: string;
  coverage_details: string;
  insured_amount: string;
  premium_amount: string;
  insurer_info_full_name: string;
  remarks: string;
  request_type: string;
  transaction_type_name: string;
  payment_plan: string;
  product: string;
  issued_policy_id: string;
  product_group: string;
  invoice_status_name: string;
  invoice_status_color: string;
  credit_period_days?: number;
  credit_age_days?: number;
  last_paid_date?: string;
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
};
