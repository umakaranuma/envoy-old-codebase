export interface ICommissionSetting {
  agent_commission_config: string;
  payment_frequency: string;
}

export const initCommissionSettings = {
  agent_commission_config: '',
  payment_frequency: '',
};

export const initApprovalPermissions = {
  policy_request_approval: false,
  quotation_request_approval: false,
};
