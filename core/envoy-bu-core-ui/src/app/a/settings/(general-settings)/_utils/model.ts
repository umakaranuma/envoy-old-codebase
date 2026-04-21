export interface ITaskConfigs {
  id?: number;
  task?: string;
  code?: string;
  task_type_id?: number;
  opportunity_status_id?: number;
  expected_days?: number;
  reminder_expected_days?: number;
  sort_index?: string;
}

export const initFormData = {
  task: '',
  // code: '',
  task_type_id: '',
  opportunity_status_id: '',
  expected_days: '',
  reminder_expected_days: '',
};
