import React from 'react';
import { formatDate, thousandSeparator } from '@/helpers/services/commonService';
import { useCurrency } from '@/contexts/CurrencyContext';

function PolicyCard({
  productName,
  policyNumber,
  // riskType,
  status,
  premiumAmount,
  startDate,
  endDate,
}: {
  productName?: string;
  policyNumber?: string;
  // riskType?: string;
  status?: { name: string; color: string };
  premiumAmount: string;
  startDate: string;
  endDate: string;
}) {
  const { currency } = useCurrency();
  return (
    <div className="p-1 d-flex flex-column gap-1">
      <div className="d-flex justify-content-between align-items-center gap-3">
        <div className="fs-13">{policyNumber}</div>
        <div className="fs-12 d-flex align-items-center justify-content-between gap-1" style={{ color: `${status?.color}` }}>
          <svg width="9" height="8" viewBox="0 0 9 8" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="4.375" cy="4" r="3" fill={status?.color} />
          </svg>
          <div>{status?.name}</div>
        </div>
      </div>
      <div className="d-flex justify-content-between align-items-center gap-3">
        <div className="fs-12"> {productName || 'N/A'}</div>
        <div className="fs-12">{`${currency.code} ${thousandSeparator(premiumAmount)}`}</div>
      </div>
      <div className="fs-12 text-muted">
        {formatDate(startDate)} to {formatDate(endDate)}
      </div>
    </div>
  );
}

export default PolicyCard;
