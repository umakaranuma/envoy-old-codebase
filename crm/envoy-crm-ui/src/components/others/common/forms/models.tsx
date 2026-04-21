export interface IElements {
  id: number;
  label: string;
  element_id: number;
  element_code: string;
  step_id: number | null;
  panel_id: number;
  parent_id: number;
  code: string;
  category: string;
  order_number: number;
  column_size: number;
  is_required: number;
  options: any[];
  value: any | null;
}

export interface IForm {
  template: Template;
  steps: Step[];
  panels: Panel[];
  elements: IElements[];
}

export interface Template {
  id: number;
  name: string;
  description: any;
  type: string;
}

export interface Step {
  id: number;
  title: string;
  step_number: number;
  description: any;
  form_id: number;
}

export interface Panel {
  id: number;
  title?: string;
  step_id?: number;
  form_id: number;
  order_number: number;
}

export interface IFormTemplate {
  template: Template;
  steps: Step[];
  panels: Panel[];
  elements: IElements[];
}
