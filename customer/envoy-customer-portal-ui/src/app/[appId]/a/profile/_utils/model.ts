export interface IJobtitle {
  title: string;
  description?: string;
}

export const initFormData = {
  title: '',
  description: '',
};

export interface IImageUploadData {
  url: string;
  preview: string;
  cropperVisible: boolean;
  key: number;
  croppedFile: File | null;
}

export const initMyDetails = {
  account_holder: '',
  bank_name: '',
  bank_branch: '',
  account_number: '',
  isbn_swift_code: '',
  estimated_amount: '',
};

export interface IProfileDetails {
  id: number;
  code: string;
  type: string;
  name: string;
  logo: string;
  remarks: string;
  parent_id: null;
  primary_contact_id: number;
  entity_id: number;
  idp_customer_id: string;
  portal_id: number;
  contact_name: string;
  contact_email: string;
  contact_address: string;
  contact_primary_contact: string;
  contact_secondary_contact: string;
  contact_remarks: null;
  contact_website_url: string;
  contact_picture: string;
  bank_detail_id: number;
  doc: string;
  doc_type: string;
  doc_name: string;
  account_holder_name: string;
  bank_name: string;
  bank_branch: string;
  account_number: string;
  iban_swift_code: string;
  created_at: Date;
  updated_at: Date;
}

export interface ILoginHistory {
  id: number;
  user_id: null;
  customer_id: number;
  login_time: string;
  device: Device;
  ip: IP;
  location: null | string;
  module: Module;
  created_at: Date;
  updated_at: Date;
  deleted_at: null;
  email: Email;
  status: Status;
}

enum Device {
  PostmanRuntime7441 = 'PostmanRuntime/7.44.1',
}

enum Email {
  CustomerEmailCOM = 'customer@email.com',
}

enum IP {
  The12323196132 = '123.231.96.132',
  The127001 = '127.0.0.1',
}

enum Module {
  Customer = 'customer',
}

enum Status {
  Active = 'active',
  Inactive = 'inactive',
}
