export const initInviteUserForm = {
  name: '',
  email: '',
  role_id: null,
};

export interface IUserInvitation {
  name: string;
  email: string;
  role_id: number | null;
}

export interface IInvitation {
  uid: string;
  name: string;
  email: string;
  role_id: number;
  role_name: string;
}

export interface IUser {
  title: string;
  id: number | null;
  first_name: string;
  last_name: string;
  display_name: string;
  email: string;
  contact_no: null | number;
  picture: string;
  role_id: number | null;
  role_name: string;
  entity_id: number | null;
  entity_type: string;
  salutation?: string;
  staff_code?: string;
  sales_team?: string;
  line_manager?: string;
  status?: string;
  created_by?: string;
  created_date?: string;
  updated_by?: string;
  updated_date?: string;
}

export const initUserData: IUser = {
  title: '',
  id: null,
  first_name: '',
  last_name: '',
  display_name: '',
  email: '',
  contact_no: null,
  picture: '',
  role_id: null,
  role_name: '',
  entity_id: null,
  entity_type: '',
};

export interface IDisplayName {
  label: string;
}

export interface ICustomersHierarchy {
  id: number;
  code?: number;
  name?: string;
  type?: string;
  parent_id?: string | null;
  children?: [];
}

export const salesTargetInitFormData = {
  month: '',
  year: '',
  month_target_amount: 0,
  year_target_amount: 0,
  user_id: 0,
};

export interface ISalesTarget {
  month?: string;
  month_target_amount?: number;
  year?: number;
  year_target_amount?: number | 0;
}

export const initTeamFormData = {
  name: '',
  description: '',
  status_id: 1,
  leader_id: null,
  manager_id: null,
  detector_id: null,
  user_ids: [],
};

export const initSingleTeamFormData = {
  user_ids: [],
};
