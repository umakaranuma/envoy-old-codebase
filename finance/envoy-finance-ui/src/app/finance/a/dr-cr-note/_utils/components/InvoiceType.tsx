import React from 'react';

function InvoiceType({ type }: { type: string }) {
  const isCredit = type === 'credit_note';

  return (
    <div className="d-inline-block">
      <span className={`badge fw-semibold p-1 ${isCredit ? 'bg-success bg-opacity-10 text-success border border-success' : 'bg-danger bg-opacity-10 text-danger border border-danger'}`}>
        <i className={`bi ${isCredit ? 'bi-arrow-down-left' : 'bi-arrow-up-right'}`}></i>
        {isCredit ? 'Cr' : 'Dr'}
      </span>
    </div>
  );
}

export default InvoiceType;
