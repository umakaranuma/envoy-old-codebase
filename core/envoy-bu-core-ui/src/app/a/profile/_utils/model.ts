export interface IJobtitle {
  title: string;
  description?: string;
}

export const initFormData = {
  title: '',
  description: '',
};

export interface IUser {
  id: number;
  team_name: string;
  title: null;
  first_name: string;
  last_name: null;
  display_name: string;
  email: string;
  contact_no: string | null;
  picture: string | null;
  cover_pic: string | null;
  street_address: string | null;
  city: string | null;
  state: string | null;
  postal_code: string | null;
  county: string | null;
  idp_user_id: string;
  role_id: number;
  entity_id: number;
  code: string;
  role_name: string;
  entity_type: string;
  status_id: null;
  status_name: null;
}
