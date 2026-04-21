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
export interface IAssignedTask {
  id?: number;
  code?: string;
  task?: string;
  description?: string;
  task_status_id?: string;
  assigned_to_id?: string;
  assigned_date?: string;
  start_date?: string;
  due_date?: string;
  sort_index?: number;
  opportunity_id?: number | string;
  opportunity_title: string;
  opportunity_code: string;
  opportunity_stage_name: string;
  opportunity_stage_color: string;
  task_status_name?: string;
  task_status_color?: string;
  assigned_user_name?: string;
  assigned_user_email?: string;
  assigned_user_contact?: string;
  task_status?: string;
  assigned_user?: string;
}

export const initFormData = {
  task: '',
  // code: '',
  task_type_id: '',
  opportunity_status_id: '',
  expected_days: '',
  reminder_expected_days: '',
};

export const initFormDataAssignedTask = {
  task: '',
  description: '',
  task_status_id: '',
  assigned_to_id: '',
  assigned_date: '',
  start_date: '',
  due_date: '',
  assigned_by_id: '',
  assigned_user: '',
  task_status: '',
  opportunity_id: '',
};

export const initTaskInteractions = {
  channel_id: '',
  date: '',
  notes: '',
  resource: '',
};
