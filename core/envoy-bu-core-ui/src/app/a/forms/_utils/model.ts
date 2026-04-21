export interface IForm {
  title: string;
  description?: string;
}

export const initFormData = {
  title: '',
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
