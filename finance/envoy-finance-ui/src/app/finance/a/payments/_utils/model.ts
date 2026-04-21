export const initFormData = {
  payment_id: '',
  invoice_no: '',
  payer_details: '',
  policy_info: '',
  amount_paid: 0,
  payment_date: '',
  transaction_type: '',
  remarks: '',
  outward_payment_type: '',
  original_payment_amount: 0,
  reason_for_reversal: '',
  credit_note_id: '',
  effective_date: '',
  credit_note_amount: 0,
  credit_note_remarks: '',
  credit_note_date: '',
  invoice_payment_type: '',
};

export interface IPayments {
  payment_id?: string;
  invoice_no?: string;
  payer_details?: string;
  policy_info?: string;
  amount_paid?: number;
  payment_date?: string;
  transaction_type?: string;
  remarks?: string;
  outward_payment_type?: string;
  original_payment_amount?: number;
  reason_for_reversal?: string;
  credit_note_id?: string;
  effective_date?: string;
  credit_note_amount?: number;
  credit_note_remarks?: string;
  credit_note_date?: string;
  invoice_payment_type?: string;
}
