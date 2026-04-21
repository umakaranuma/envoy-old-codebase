export const initFormData = {
  invoice_no: '',
  service_provider_id: '',
  service_type: '',
  service_id: '',
  service_date: '',
  standard_fee: null,
  invoice_status: '',
  payment_status: '',
  remarks: '',
  customer_id: '',
  service_provider_name: '',
};

export interface IServiceRendered {
  invoice_no: string;
  service_provider_id: string;
  service_type: string;
  service_id: string;
  service_date: string;
  standard_fee: number | null;
  invoice_status: string;
  payment_status: string;
  remarks: string;
}

export interface ServiceRenderedDetails {
  invoice_id: string;
  customer_name: string;
  invoice_number: string;
  outstanding_amount: number;
  vendor_name: string;
  service_provider_id: string;
  service_title: string;
  fee: number;
  invoice_status_name: string;
  payment_status_name: string;
  service_id: string;
  service_date: string;
  standard_fee: number | null;
  invoice_status: string;
  payment_status_color: string;
  remarks: string;
  createdBy: string;
  createdDate: string;
  updatedBy: string;
  updatedDate: string;
}
