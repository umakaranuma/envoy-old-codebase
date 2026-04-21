const initialBankDetail: IBankDetail = {
  account_holder_name: '',
  bank_name: '',
  bank_branch: '',
  account_number: '',
  iban_swift_code: '',
  payment_gateway_url: '',
};

export const initialContactDetail: IContactDetail = {
  role: '',
  title: '',
  is_primary: false,
  name: '',
  email: '',
  primary_contact: '',
  remarks: '',
};

export const initPartner: Company = {
  id: '',
  name: '',
  logo: '',
  address: '',
  contact_no: '',
  email: '',
  website: '',
  fax_no: '',
  status_id: 1,
  description: '',
  bank_details: [initialBankDetail],
  contact_details: [initialContactDetail],
};

export interface IBankDetail {
  id?: number;
  account_holder_name: string;
  bank_name: string;
  bank_branch: string;
  account_number: string;
  iban_swift_code: string;
  payment_gateway_url: string;
}

export interface IContactDetail {
  id?: number;
  role: string;
  title: string;
  is_primary: boolean;
  name: string;
  email: string;
  primary_contact: string;
  remarks: string;
}

export interface Company {
  id: string;
  user_id?: number;
  name: string;
  logo: string;
  address: string;
  contact_no: string;
  email: string;
  website: string;
  fax_no: string;
  status_id: number;
  description: string | null;
  created_by_id?: number;
  updated_by_id?: number;
  bank_details: IBankDetail[];
  contact_details: IContactDetail[];
}

export const initCPartner = {
  name: '',
  logo: '',
  address: '',
  contact_number: '',
  email: '',
  website: '',
  fax_no: '',

  // Bank details
  account_holder_name: '',
  bank_name: '',
  bank_branch: '',
  account_number: '',
  iban_swift_code: '',
  payment_gateway_url: '',

  // Contact details
  contact_title: '',
  contact_name: '',
  contact_primary: '',
  contact_email: '',
  contact_remarks: '',
  is_primary: false,
  contact_role: '',
  contact_type: 'primary',
};
