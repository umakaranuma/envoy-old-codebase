export interface CommissionPercent {
  value: number;
  type: string;
  user_name?: string;
  user_email?: string;
  user_id?: string;
  role_name?: string;
}

export interface ICommissionData {
  id: string;
  product_id: number;
  native_product_id: number;
  product_name: string;
  product_group_name: string;
  product_group_id: string;
  insurer: any;
  transaction_type: string;
  transaction_type_name: string;
  brokerage_revenue_percent: string;
  brokerage_revenue_type: string;
  agent_commission_percent: string;
  agent_commission_type: string;
  teams: ITeam[];
}
export interface ITeam {
  id: number;
  name: string;
}
export interface IInsurerProduct {
  id: number;
  name: string;
  code: string;
  category_id: number;
  vendor_id: number;
  coverage_level: string;
  description: string;
  currency_id: number;
  premium_amount: number | null;
  deductible_amount: number | null;
  claim_amount: number | null;
  remarks: string;
  entity_id: number | null;
  currency: string;
  type: string;
  insurer: string;
}
export interface IFormData {
  product_name: string;
  vendor_id: string;
  id: string;
  transaction_id: string;
  transaction_type: string;
  commission_type: string;
  commission_value: string;
  brokerage_commission_value: string;
  brokerage_commission_type: string;
  revised_commission_percent: IrevisedData[];
}

export interface IrevisedData {
  team_id: string;
  user_id: string;
  value: string;
  type: string;
}

export const initCommissionData = {
  brokerage_commission_type: 'fixed',
  brokerage_commission_value: '',
  commission_type: 'fixed',
  commission_value: '',
  transaction_type: '',
  transaction_id: '',
};

export interface CommissionSetupFormData {
  product_id: string;
  insurer_id: string;
  native_product_id: string;
  transaction_type: string;
  sales_team_ids?: string[];
  brokerage_revenue_percent: CommissionPercent[];
  agent_commission_percent: CommissionPercent[];
  revised_commission_percent: IrevisedData[];
  commission_percent: any[];
}

export interface ICommon {
  transaction_id: string;
  transaction_type: string;
  commission_type: string;
  commission_value: string;
  brokerage_commission_value: string;
  brokerage_commission_type: string;
}

export interface UIFormData {
  product_name: string;
  insurer_id: string;
  transaction_type: string;
  sales_team_ids?: string[];
  commission_type: string;
  commission_value: string;
  brokerage_commission_value: string;
  brokerage_commission_type: string;
  showSalesTeamList: boolean;
  commission_percent: any[];
}

export const initUIFormData: UIFormData = {
  product_name: '',
  insurer_id: '1',
  transaction_type: '',
  sales_team_ids: [],
  commission_percent: [],
  commission_type: 'fixed',
  commission_value: '',
  brokerage_commission_value: '',
  brokerage_commission_type: 'fixed',
  showSalesTeamList: false,
};
