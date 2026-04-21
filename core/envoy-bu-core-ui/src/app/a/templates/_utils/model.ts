export const initFormData = {
  title: '',
  type: 'single_form',
  description: '',
};

export interface IAttribute {
  title: string;
  type: string;
  description?: string;
}

export const initAttributeFormData = {
  title: '',
  type: 'TEXT ',
  description: '',
};

export const initElementFormData = {
  id: '',
  label: '',
  element_id: '',
  element_code: '',
  step_id: '',
  panel_id: '',
  order_number: 0,
  column_size: 12,
  column_size_label: '100%',
  is_required: false,
  options: [],
  value: '',
  category: '',
  parent_id: null,
  code: '',
};

export interface IFormElement {
  id: string;
  label: string;
  element_id: string;
  element_code: string;
  step_id: string;
  panel_id: string;
  order_number: number;
  column_size: number;
  is_required: boolean;
  options: any[];
  value: any;
  category: string;
  parent_id: string | null;
  code: string;
}

export interface IFormElementGroup {
  group: string;
  elements: IFormElement[];
}

export interface ITemplate {
  title: string;
  type: string;
}

export interface IResult {
  template: ITemplate;
  steps: IStep[];
  panels: IPanel[];
  elements: IElement[];
}

export interface ITemplate {
  id: number;
  name: string;
  description: string | null;
  type: string;
}

export interface IStep {
  id: number;
  title: string;
  description: string | null;
  step_number: number;
  form_id: number;
}

export interface IPanel {
  id: number;
  title: string;
  step_id: number;
  form_id: number;
  order_number: number;
}

export interface IElement {
  id: number;
  label: string;
  step_id: number;
  form_id: number;
  order_number: number;
  panel_id: number;
  code: string;
  options?: any[];
  value?: any;
  column_size: any;
  is_required: any;
  category: string;
  parent_id: number;
}
