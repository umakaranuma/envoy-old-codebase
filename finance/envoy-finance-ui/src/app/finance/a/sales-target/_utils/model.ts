const currentDate = new Date();
const currentMonth = currentDate.getMonth() + 1;
const currentYear = currentDate.getFullYear();

export const years = Array.from({ length: 6 }, (_, i) => ({
  label: new Date().getFullYear() + i,
  value: new Date().getFullYear() + i,
}));

export const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

export const initFormData = {
  team_id: [],
  agent_id: [],
  period_type: 'monthly',
  month: currentMonth,
  year: currentYear,
  target_amount: '',
  isNewColumn: false,
  isTargetSet: false,
  parentIndex: undefined,
};

export interface ISalesTargetResult {
  id: number;
  period_type: string;
  month: number;
  year: number;
  target_amount: string;
  agent_id: number;
  agent_name: string;
  agent_email: string;
  team_name: string;
  achieved: number;
}

export const emptyTargetResult: ISalesTargetResult = {
  id: 0,
  period_type: '',
  month: 0,
  year: 0,
  target_amount: '0.00',
  agent_id: 0,
  agent_name: '',
  agent_email: '',
  team_name: '',
  achieved: 0.0,
};
