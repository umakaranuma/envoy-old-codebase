export interface IClaimTemplate {
  template: Template;
  steps: Step[];
  panels: Panel[];
  elements: IElement[];
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
  step_number?: number;
  description?: any;
  form_id?: number;
}

export interface Panel {
  id: number;
  title?: string;
  step_id?: number;
  form_id: number;
  order_number: number;
}

export interface IElement {
  id: number;
  label?: string;
  is_required: number;
  order_number: number;
  column_size: number;
  panel_id: number;
  step_id: number;
  element_id: number;
  code: string;
  value?: string;
  options: Option[];
}

export interface Option {
  id: number;
  option_value: string;
  element_id: number;
}

export const initStepData = [
  {
    id: 1000,
    title: 'Policyholder Info',
  },
  {
    id: 1001,
    title: 'Policy Info',
  },
];
