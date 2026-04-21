export const initFormData = {
  id: '',
  reason: '',
  type: '',
  allows_custom_reason: false,
  description: '',
  type_id: '',
};
export interface IReasonData {
  id?: string;
  reason?: string;
  type?: string;
  type_id?: string;
  allows_custom_reason?: boolean;
  description?: string;
}
