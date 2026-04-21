export interface IContacts {
  title: string;
  name: string;
  email?: string;
  address?: string;
  primary_contact: string;
  secondary_contact?: number;
  remarks?: string;
  picture?: string;
  merged_contacts: IContacts[];
}

export interface IInteractions {
  notes?: string;
  channel?: string;
  contact_by?: string;
  date?: string;
  interaction_type?: string;
  task?: string;
  imitated_by?: string;
}

export const initFormData = {
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

export interface IContactGroup {
  name: string;
  description: string;
  contacts: string[];
}

export const initCreateGroupFormData = {
  name: '',
  description: '',
  contacts: [],
};
