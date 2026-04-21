export interface IPayments {
  name?: string;
  description?: string;
}

export interface IBrokerageCommissionResult {
  id: number;
  brokerage_commission_id: number;
  agent_id: number;
  agent_commission_percent: string;
  agent_commission_type: string;
  revised_amount_percent: string;
  revised_amount_type: string;
  target_achievement_amount: string;
  revised_amount: string;
  revenue_recognized: string;
  revenue_realized: string;
  paid_amount: string;
  status: string;
  entity_id: number;
  commission_setup_id: number;
  created_at: string;
  created_by: string;
  created_by_logo: string | null;
  brokerage_revenue_percent: string;
  brokerage_revenue_recognized: string;
  brokerage_revenue_realized: string;
  overriding_commission_amount: string;
  total_agent_commission: string;
  invoice_number: string;
  invoice_amount: string;
  last_paid_date: string;
  brokerage_policy_id: string;
  premium_amount: string;
  policy_effective_date: string;
  end_date: string;
  sales_team_id: number;
  insurer_id: number;
  product_id: number;
  user_name: string;
  team_name: string;
  insurer_name: string;
  product_name: string;
  outstanding: string;
  commission_deductible?: string;
}

export interface IIncentiveData {
  id: string;
  // Add other fields your card needs here
  // For example:
  // name: string;
  // amount: number;
  // etc.
}

export const initFormData = {
  name: '',
  description: '',
  performance_fields: {
    logic: '',
    conditions: [],
  },
  reward_type: 'fixed',
  reward_type_id: 1,
  reward_type_value: '',
  repeation_type: '',
  start_date: '',
  end_date: '',
};

export interface IPerformanceField {
  field: string;
  type: string;
  operators: string[];
  widget: string;
  description: string;
  aggregation?: string;
}

export type LogicType = 'AND' | 'OR';

export interface ConditionNode {
  field: string;
  operator: string;
  value: any;
  reward_type?: 'fixed' | 'percentage';
  reward_type_value?: number;
}

export interface LogicGroupNode {
  logic: LogicType;
  conditions: LogicNode[];
  reward_type?: 'fixed' | 'percentage';
  reward_type_value?: number;
}

export type LogicNode = ConditionNode | LogicGroupNode;

export interface IIncentive {
  id: number;
  name: string;
  description: string;
  repeation_type: string;
  start_date: string;
  end_date: string;
  reward_type_value: number;
  performance_fields: any;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
  incentive_base_field: string | null;
  reward_type_id: number;
  reward_type_name: string;
}

export const emptyIncentive: IIncentive = {
  id: 0,
  name: '',
  description: '',
  repeation_type: '',
  start_date: '',
  end_date: '',
  reward_type_value: 0,
  performance_fields: '',
  created_at: '',
  updated_at: '',
  deleted_at: null,
  incentive_base_field: null,
  reward_type_id: 0,
  reward_type_name: '',
};
