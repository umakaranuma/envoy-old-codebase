import { getAllClaims } from './api-service';

export async function fetchClaimsTableData({ searchValue, currentPage, itemsPerPage, sortBy, sortDir }: any) {
  const response = await getAllClaims({
    search: searchValue.toLowerCase(),
    page: currentPage,
    limit: itemsPerPage,
    sort_by: sortBy,
    sort_dir: sortDir,
  });

  if (response.is_success) {
    return { data: response.result.data || [], dataLength: response.result.total_records || 0 };
  }
}

export const claimData = {
  claimData: {
    headers: ['Converged Details', 'Estimated Amount', 'Aggremed Amount', 'Payable by Instant (50%)', 'Payable by Customer (20%)'],
    rows: [
      {
        details: 'Bodily Injury Liability',
        estimated: 'LKR 5,000',
        aggremed: 'LKR 4,000',
        payableInstant: 'LKR 3,700',
        payableCustomer: 'LKR 800',
      },
      {
        details: 'Medical Payments',
        estimated: 'LKR 2,500',
        aggremed: 'LKR 2,000',
        payableInstant: 'LKR 1,600',
        payableCustomer: 'LKR 400',
      },
      {
        details: 'Towing and Labor',
        estimated: 'LKR 500',
        aggremed: 'LKR 400',
        payableInstant: 'LKR 320',
        payableCustomer: 'LKR 80',
      },
      {
        details: 'Vehicle Damage',
        estimated: 'LKR 10,000',
        aggremed: 'LKR 8,000',
        payableInstant: 'LKR 6,400',
        payableCustomer: 'LKR 1,600',
      },
      {
        details: 'Property Damage',
        estimated: 'LKR 3,000',
        aggremed: 'LKR 2,500',
        payableInstant: 'LKR 2,000',
        payableCustomer: 'LKR 500',
      },
    ],
    totals: {
      estimated: 'LKR 21,000',
      aggremed: 'LKR 16,900',
      payableInstant: 'LKR 13,520',
      payableCustomer: 'LKR 3,350',
    },
    totalClaimAmount: 'LKR 13,520',
  },
};
