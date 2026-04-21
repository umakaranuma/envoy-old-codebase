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
        <div className="fs-12"> {productName}</div>
        <div className="fs-12">{`${currency.code} ${thousandSeparator(premiumAmount)}`}</div>
      </div>
      <div className="fs-12 text-muted">
        {formatDate(startDate)} to {formatDate(endDate)}
      </div>
    </div>
  );
}

export default PolicyCard;

{
  /* <div className="text d-flex align-items-center gap-2 p-1"> */
}
{
  /* <S3Avatar imageKey={picture || ''} width={40} height={40} className="m-1" /> */
}
{
  /* <div>
        <div className="d-flex flex-row gap-2">
          {policyNumber} */
}
{
  /* <Badge text={policyNumber} variant="outline" color="primary" radius="pill" /> */
}
{
  /* {productName} */
}
{
  /* <Badge text={policyNumber} variant='outline' color='primary' radius='pill' /> */
}
{
  /* <Badge text={riskType} variant="light" color="secondary" /> */
}
// </div>
{
  /* <div className="text-muted mt-1">
          <div className="d-flex flex-row gap-2">
            {name}
            <Badge text={policyNumber} variant="outline" color="primary" radius="pill" />
          </div>
          <Flexicon icon="phone" variant="line" size={14} className="text-primary me-1" />
          <span className="fs-12">{contactNumber || '-'}</span>
          <span className="fs-12"> | </span>
          <Flexicon icon="mail-01" variant="line" size={14} className="text-primary me-1" />
          <span className="fs-12">{contactEmail || '-'}</span>
        </div> */
}
//   </div>
// </div>
