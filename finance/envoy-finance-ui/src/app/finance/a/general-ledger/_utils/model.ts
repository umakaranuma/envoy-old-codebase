export interface IGeneralLedgerAccount {
  account_name: string;
  account_type: 'asset' | 'liability' | 'equity' | 'revenue' | 'expense';
  balance: number;
  description?: string;
}

export const initFormData = {
  account_name: '',
  account_type: '',
  description: '',
};

export interface IAccountType {
  name: string;
  description: string;
  accounts: string[];
}

export const initCreateAccountTypeFormData = {
  name: '',
  description: '',
  accounts: [],
};

export interface IInsurancePolicy {
  customer_name: string;
  insurer_name: string;
  agent_name: string;
  customer_id: string;
  insurer_id: string;
  agent_id: string;
  policy_name: string;
  policy_id: string;
  policy_type: string;
}

export const initInsurancePolicyFormData = {
  customer_name: '',
  insurer_name: '',
  agent_name: '',
  customer_id: '',
  insurer_id: '',
  agent_id: '',
  policy_name: '',
  policy_id: '',
  policy_type: '',
};

export interface ISample {
  title: string;
  name: string;
  email?: string;
  address?: string;
  primary_contact: string;
  secondary_contact?: number;
  remarks?: string;
  picture?: string;
  merged_contacts: ISample[];
  is_primary: boolean;
}

export type ChartType = 'pie' | 'bar' | 'line' | 'area';
