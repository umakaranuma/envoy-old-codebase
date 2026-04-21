import { getCurrency } from '@/helpers/services/currencyService';
import React from 'react';

export default function MyCommissionCard({ title, amount }: { title: string; amount: string }) {
  const currency = getCurrency();
  return (
    <div className="d-flex justify-content-center mt-1 mt-md-4">
      <div className="card p-3 text-start shadow-sm border-0" style={{ minWidth: '280px' }}>
        <div className="card-body p-0">
          <div className="d-flex justify-content-between align-items-center mb-3">
            <div className="text-muted text-uppercase small fw-semibold">{title}</div>
            <div className="my-commission rounded-2">{currency.code}</div>
          </div>
          <div className="h4 fw-bold mb-0">{amount}</div>
        </div>
      </div>
    </div>
  );
}
