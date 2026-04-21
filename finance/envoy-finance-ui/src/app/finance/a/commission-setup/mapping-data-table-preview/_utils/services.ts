interface MappingDataTablePreview {
  id: string;
  product_name: string;
  insurer_info: string;
  transaction_type: string;
  sales_team: string;
  commission_percentage: number;
  revised_commission_percentage: number;
  target_achievements_commission_percentage: number;
}

const sampleMappingDataTablePreview: MappingDataTablePreview[] = [
  {
    id: '1',
    product_name: 'Health Shield Plus',
    insurer_info: 'ABC Insurance Co.',
    transaction_type: 'New Policy',
    sales_team: 'Team A',
    commission_percentage: 10,
    revised_commission_percentage: 12,
    target_achievements_commission_percentage: 15,
  },
  {
    id: '2',
    product_name: 'Life Secure Plan',
    insurer_info: 'XYZ Life Insurance',
    transaction_type: 'Renewal',
    sales_team: 'Team B',
    commission_percentage: 8,
    revised_commission_percentage: 9,
    target_achievements_commission_percentage: 11,
  },
  {
    id: '3',
    product_name: 'Auto Protect',
    insurer_info: 'DriveSafe Ltd.',
    transaction_type: 'Upgrade',
    sales_team: 'Team C',
    commission_percentage: 6,
    revised_commission_percentage: 7,
    target_achievements_commission_percentage: 9,
  },
  {
    id: '4',
    product_name: 'Home Guard Policy',
    insurer_info: 'SecureHome Insurance',
    transaction_type: 'New Policy',
    sales_team: 'Team D',
    commission_percentage: 7,
    revised_commission_percentage: 8,
    target_achievements_commission_percentage: 10,
  },
];
// GET ALL MappingDataTablePrevie
export async function getAllMappingDataTablePreview() {
  return {
    is_success: true,
    result: {
      data: sampleMappingDataTablePreview,
      total_records: sampleMappingDataTablePreview.length,
    },
  };
}

// TABLE data fetcher
export async function fetchAllMappingDataTablePreview() {
  const response = await getAllMappingDataTablePreview();

  if (response.is_success) {
    return {
      data: response.result.data,
      dataLength: response.result.total_records,
    };
  }

  return {
    data: [],
    dataLength: 0,
  };
}
