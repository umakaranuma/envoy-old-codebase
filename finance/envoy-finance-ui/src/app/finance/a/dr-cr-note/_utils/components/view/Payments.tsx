'use client';
import React, { useState } from 'react';
import PaymentList from './PaymentList';
import CreatePayment from './CreatePayment';

function Payment() {
  const [tableVers, setTableVers] = useState(0);
  const [_createFormKey, setCreateFormKey] = useState(0);
  const [createFormVisible, setCreateFormVisible] = useState(false);
  const [currentViewId, _setCurrentViewId] = useState('');
  const [paymentData, _setPaymentData] = useState({
    id: '',
    invoiceNumber: '',
    totalAmount: 0,
    outstandingAmount: 0,
  });

  const handleCreateFormOnCancel = () => {
    setCreateFormVisible(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterSave = () => {
    setTableVers((prevTableVers) => prevTableVers + 1);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  return (
    <>
      <PaymentList invoiceId={currentViewId} tableVersion={tableVers} />

      {currentViewId !== '' && <CreatePayment isOpen={createFormVisible} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} invoiceData={paymentData} />}
    </>
  );
}

export default Payment;
