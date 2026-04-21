export interface InsurerProduct {
  id: string;
  code: string;
  insurer: string;
  name: string;
  type: string;
  coverage_level: string;
  description: string;
  currency: string;
  premium_amount: number;
  deductible_amount: number;
  claim_limit: number;
  last_updated_date: string;
  remarks: string;
}

export interface NativeProduct {
  id: string;
  name: string;
  risk_type: string;
  code: string;
}
