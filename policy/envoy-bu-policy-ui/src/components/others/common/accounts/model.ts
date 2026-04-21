interface IPrimaryContact {
  name: string;
  primary_contact: string;
  secondary_contact: string | null;
  email: string;
  address: string;
  picture: string | null;
  duplicated_contact_id: number | null;
  website_url: string | null;
}
export interface ICustomers {
  id: number;
  code: number;
  entity_id: string;
  type?: string;
  name?: string;
  logo?: string;
  remarks?: string;
  parent_id?: string | null;
  primary_contact_id_id?: number;
  primary_contact: IPrimaryContact;
  email?: string;
}

export interface ICustomersHierarchy {
  id: number;
  code?: number;
  name?: string;
  type?: string;
  parent_id?: string | null;
  children?: [];
}

export interface IType {
  label: string;
}

export const initFormData = {
  id: '',
  type: '',
  code: '',
  name: '',
  remarks: '',
  parent_id: null as string | null,
  primary_contact_id_id: '',
  primary_contact: '',
  website_url: '',
  address: '',
  email: '',
  secondary_contact: '',
  contact_id: '',
  flex_fields: {} as Record<string, string>,
};

export const initContactFormData = {
  title: '',
  name: '',
  email: '',
  address: '',
  primary_contact: '',
  secondary_contact: '',
  remarks: '',
  picture: '',
  merged_contacts: [],
  contact_id: '',
};
