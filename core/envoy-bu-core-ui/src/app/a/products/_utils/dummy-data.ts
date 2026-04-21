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

export interface DummyData {
  nativeProducts: NativeProduct[];
  // insurerProducts: Record<string, InsurerProduct[]>;
}

export const dummyData: DummyData = {
  nativeProducts: [
    {
      id: '1',
      name: 'Health Insurance Package',
      risk_type: 'Health',
      code: 'HIP001',
    },
    {
      id: '2',
      name: 'Auto Insurance Bundle',
      risk_type: 'Automotive',
      code: 'AIB002',
    },
    {
      id: '3',
      name: 'Property Insurance Set',
      risk_type: 'Property',
      code: 'PIS003',
    },
  ],
};
