export const initNativeProduct = {
  name: '',
  risk_type: '',
  native_product_name: '',
  insurer_info: '',
  product: [
    {
      policy_terms_and_conditions: false,
      product_name: '',
      insurer_info: '',
    },
  ],
};

export type ApiResponse<T> = {
  is_success: boolean;
  result: T;
  message?: string;
  status_code?: number;
};

export type InsurerProduct = {
  vendor_id: string;
  vendor_name?: string;
  product_id: string;
  product_name?: string;
};

export type FormData = {
  name: string;
  category_id: string;
  insurer_products: InsurerProduct[];
  type?: string;
  opportunity_type_id: string;
};

export type SelectOption = {
  label: string;
  value: string;
};

export type IProductItem = {
  name: string;
  type_id: string;
  type: string;
  description: string;
  id: string;
};

export const initProductItem = {
  name: '',
  type_id: '',
  type: '',
  description: '',
  id: '',
};

export type IDocument = {
  name: string;
  is_mandatory: boolean;
  type: string;
  id?: string | number;
};

export const initDocument = {
  name: '',
  is_mandatory: false,
  type: '',
};

export const initInsurerProdut = {
  name: '',
  category_id: null,
  vendor_id: null,
  coverage_level: '',
  description: '',
  currency_id: null,
  date: new Date().toISOString().split('T')[0],
  remarks: '',
  docs: '',
  doc_name: '',
  doc_type: '',
};

export type IProductGroupFormData = {
  name: string;
  native_products: string[];
  teams: any[];
  id: string;
};

export const initProductGroup = {
  name: '',
  product_ids: [],
  team_ids: [],
  currency_id: '',
  currency_code: '',
};

export interface IInsurerProduct {
  id: number;
  name: string;
  code: string;
  category_id: number;
  vendor_id: number;
  coverage_level: string;
  description: string;
  currency_id: number;
  premium_amount: number | null;
  deductible_amount: number | null;
  claim_amount: number | null;
  date: string;
  remarks: string;
  added_by: string;
  docs: string;
  entity_id: number;
  currency: string;
  type: string;
  insurer: string;
  doc_name: string;
  doc_type: string;
  is_mapped_to_native_product: boolean;
  native_product_id: number | null;
  native_product: any | null;
}

export const initInsurerProduct: IInsurerProduct = {
  id: 0,
  name: '',
  code: '',
  category_id: 0,
  vendor_id: 0,
  coverage_level: '',
  description: '',
  currency_id: 0,
  premium_amount: null,
  deductible_amount: null,
  claim_amount: null,
  date: '',
  remarks: '',
  added_by: '',
  docs: '',
  entity_id: 0,
  currency: '',
  type: '',
  insurer: '',
  doc_name: '',
  doc_type: '',
  is_mapped_to_native_product: false,
  native_product_id: 0,
  native_product: null,
};
