export interface IClaimEvaluationInfo {
  claim_id: number;
  claim_code: string;
  claim_status: string;
  claim_status_color: string;
  template: Template;
  steps: any[];
  panels: Panel[];
  elements: Element[];
}

export interface Element {
  id: number;
  label: string;
  is_required: number;
  order_number: number;
  column_size: number;
  panel_id: number;
  step_id: null;
  element_id: number;
  category: string;
  code: string;
  parent_id: null;
  element_code: string;
  value: string;
  options: Option[];
}

export interface Option {
  id: number;
  option_value: string;
  element_id: number;
}

export interface Panel {
  id: number;
  title: null;
  step_id: null;
  form_id: number;
  order_number: number;
}

export interface Template {
  id: number;
  name: string;
  description: string;
  type: string;
}
