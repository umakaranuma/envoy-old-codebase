export interface IOpportunity {
  id: number | null;
  title: string;
  type: string;
  contact_info_type: string;
  customer_id: number | null;
  stage_id: number | null;
  currency_id: number | null;
  sales_agent_id: number | null;
  channel_id: number | null;
  campaign_id: number | null;
  contact_number: string;
  email: string;
  code: string;
  last_contacted_date: string;
  remarks: string;
  sort_index: string;
  contact_id: number | null;
  created_by_id: number | null;
  entity_id: string | null;
  current_health_id: number | null;
  channel_name: string;
  currency_name: string;
  opportunity_type_id: any | null;
  sales_agent_picture: string;
  sales_agent_name: string;
  account_manager_id: string;
  account_manager_name: string;
  stage_color?: string;
  stage_name?: string;
  stage_type?: string;
  entity: EntityData;
  quotation_id?: string;
}
export interface EntityData {
  created_by_name: string;
  updated_by_name: string;
  created_at: string;
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
  last_contacted_date: '',
  remarks: '',
  sort_index: '',
  contact_id: null,
  created_by_id: null,
  entity_id: null,
  current_health_id: null,
  channel_name: '',
  currency_name: '',
  opportunity_type_id: [],
  sales_agent_name: '',
  sales_agent_picture: '',
  account_manager_id: '',
  account_manager_name: '',
  stage_color: '',
  stage_name: '',
  stage_type: '',
  entity: {} as EntityData,
};
