export const initFormData = {
  name: '',
  description: '',
};

export interface IPayments {
  name?: string;
  description?: string;
}

export interface IBrokerageCommissionResult {
  id: number;
  brokerage_commission_id: number;
  agent_id: number;
  agent_name: string;
  agent_email: string | null;
  agent_picture: string | null;
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
  status_color?: string;
  credit_period_days?: number;
}
