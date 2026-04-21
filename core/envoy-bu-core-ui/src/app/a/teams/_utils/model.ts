export const initTeamFormData = {
  name: '',
  description: '',
  status_id: 1,
  manager_id: '',
  detector_id: null,
  user_ids: [],
  product_ids: [],
  leader_id: null,
  manager_name: '',
};

export interface ITeam {
  id: number;
  name: string;
  description: string;
  status_id: number;
  status_name: string;
  leader_id: null;
  leader_name: null;
  manager_id: number;
  manager_name: string;
  detector_id: null;
  detector_name: null;
  created_at: Date;
  sales_agents: SalesAgent[];
  products: Product[];
}

export interface Product {
  id: number;
  name: string;
  code: string;
  category_id: number;
  created_at: Date;
}

export interface SalesAgent {
  id: number;
  display_name: string;
  email: string;
  picture: null | string;
  code: string;
  contact_no: null;
  role_name: string;
}
