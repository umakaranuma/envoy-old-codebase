export interface IOpportunity {
  id: number | null;
  title: string;
  type: string;
  contact_info_type?: string;
  contact_number: string | null;
  email: string | null;
  code: string;
  last_contacted_date: string | null;
  campaign_id: number | null;
  remarks: string | null;
  sort_index: number;
  lead_value: number | null;
  sale_value: number | null;
  account_manager_id: number | null;
  channel_id: number | null;
  contact_id: number | null;
  country_id: number | null;
  created_by_id: number | null;
  currency_id: number | null;
  customer_id: number | null;
  entity_id: number | null;
  sales_agent_id: number | null;
  current_health_id: number | null;
  stage_id: number | null;
  transaction_type: string;
  issued_policy_id: number | null;
  stage_name: string;
  stage_type: string;
  stage_color: string;
  sales_agent_name: string;
  sales_agent_picture: string | null;
  currency_name: string;
  currency_symbol: string;
  account_manager_name: string | null;
  account_manager_picture: string | null;
  channel_name: string | null;
  quotation_id: number | null;
  country_name: string | null;
  country_code: string | null;
  customer_name: string;
  customer_logo: string;
  customer_type: string;
  customer_contact_name: string;
  customer_contact_email: string;
  customer_contact_phone: string;
  customer_contact_address: string;
  health_id: number | null;
  health_value: number | null;
  health_date: string | null;
  health: {
    id: number | null;
    value: number | null;
    date: string | null;
  };
  entity: EntityData;
  // Legacy/additional fields for form handling
  opportunity_type_id?: any | null;
  current_health?: string;
  request_type_label?: string;
  opportunity_types?: Array<{ id: string; name: string }>;
  contact_name?: string;
  opportunity_id?: number | null;
  product_name?: string;
  product_group_name?: string;
}

export interface EntityData {
  id: number;
  type: string;
  created_by_id: number;
  created_by_name: string;
  created_by_profile: string | null;
  updated_by_id: number;
  updated_by_name: string;
  updated_by_profile: string | null;
  created_at: string;
  notes: any[];
  documents: any[];
}

export const initFormData = {
  id: null,
  title: '',
  type: 'Personal',
  contact_info_type: 'manual',
  customer_id: null,
  stage_id: null,
  currency_id: null,
  sales_agent_id: null,
  channel_id: null,
  campaign_id: null,
  contact_number: '',
  email: '',
  code: '',
  last_contacted_date: new Date().toISOString().split('T')[0],
  remarks: '',
  sort_index: '',
  contact_id: null,
  created_by_id: null,
  entity_id: null,
  current_health_id: null,
  channel_name: '',
  currency_name: '',
  opportunity_type_id: [],
  salse_agent_name: '',
  sales_agent_picture: '',
  account_manager_id: '',
  account_manager_name: '',
  stage_color: '',
  stage_name: '',
  stage_type: '',
  lead_value: null,
  sale_value: null,
  country_id: null,
  country_name: '',
  entity: {} as EntityData,
  transaction_type: 'new',
  currency_code: '',
  current_health: '',
  request_type_label: 'New',
  opportunity_types: [],
  contact_name: '',
  customer_name: '',
  opportunity_id: null,
  sales_agent_name: '',
  issued_policy_id: null,
  product_name: '',
  product_id: '',
};

export interface IContacts {
  title: string;
  name: string;
  email?: string;
  address?: string;
  primary_contact: number;
  secondary_contact?: number;
  remarks?: string;
  picture?: string;
  merged_contacts?: IContacts[];
}

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
};

export interface ICustomers {
  id: number;
  code: number;
  type?: string;
  name?: string;
  br_no?: number;
  address?: string;
  email?: string;
  primary_contact?: number;
  secondary_contact?: number;
  logo?: string;
  website?: string;
  no_of_employees?: number;
  remarks?: string;
  parent_id?: number;
  primary_contact_id?: number;
}

export interface IType {
  id: string;
  title: string;
  description: string;
}

export interface IHealth {
  id: number;
  date: Date;
  health: number;
  opportunity_id: number;
}
export interface INotes {
  id?: string;
  is_high_priority?: number;
  notes: string;
}

export const initNotesFormData: INotes = {
  id: '',
  is_high_priority: 0,
  notes: '',
};

export const initInteractionData = {
  channel_id: '',
  notes: '',
  resource: '',
  contact_by_id: '',
  date: '',
  channel_name: '',
  contact_by_first_name: '',
  contact_name: '',
  contact_id: '',
  name: '',
};

export interface IInteraction {
  id: string;
  opportunity_id: string;
  date: string;
  notes: string;
  opportunity_status_id: string;
  channel_id: string;
  contact_id: string;
  contact_by_id: string;
  contact_by_display_name: string;
  customer_id: string;
  task_id: string;
  channel_name: string;
  contact_name: string;
  customer_name: string;
  contact_by_first_name: string;
  contact_by_last_name: string;
  task_title: string;
  opportunity_status_name: string;
  entity_id: string;
}

export interface IDocument {
  id: string;
  doc: string;
  name: string;
  type: string;
}

export const initFlagData = {
  flag_id: null,
  reason_id: null,
  customer_reason: '',
  remarks: '',
};

export interface IFlag {
  id: string;
}

export interface IFlagResons {
  id: string;
  name: string;
  description: string;
  color: string;
}

export interface IEntities {
  id: string;
  type: string;
  created_by_id: string;
  updated_by_id: string;
  created_at: string;
  created_by_name: string;
  created_by_profile: string;
  updated_by_name: string;
  updated_by_profile: string;
  flags: IFlagResons[];
}

export interface IResons {
  allows_custom_reason: number;
  description: string;
  reason: string;
  type: string;
}

export interface Activity {
  id: number;
  activity: string;
  entity_id: number;
  added_at: string;
  added_by_id: number | null;
  added_by_name: string;
  added_by_picture: null;
}

export interface ActivityResult {
  total_records: number;
  per_page: number;
  current_page: number;
  last_page: number;
  data: Activity[];
}

export interface IElements {
  id: number;
  label: string;
  element_id: number;
  element_code: string;
  step_id: number | null;
  panel_id: number;
  parent_id: number;
  code: string;
  category: string;
  order_number: number;
  column_size: number;
  is_required: number;
  options: any[];
  value: any | null;
}

export interface IForm {
  template: Template;
  steps: Step[];
  panels: Panel[];
  elements: IElements[];
}

export interface Template {
  id: number;
  name: string;
  description: any;
  type: string;
}

export interface Step {
  id: number;
  title: string;
  step_number: number;
  description: any;
  form_id: number;
}

export interface Panel {
  id: number;
  title?: string;
  step_id?: number;
  form_id: number;
  order_number: number;
}
