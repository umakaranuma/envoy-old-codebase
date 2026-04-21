export interface IOpportunityType {
  name?: string;
  title: string;
  description?: string;
}

export const initFormData = {
  form_id: '',
  data_gethering_type: 'ONBOARDING',
  opportunity_type_id: '',
  title: '',
  description: '',
};

export interface IForm {
  title: string;
  type: string;
  description?: string;
}
