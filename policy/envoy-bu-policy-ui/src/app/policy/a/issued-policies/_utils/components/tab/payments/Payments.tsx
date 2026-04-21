'use client';
import React, { useState } from 'react';
import PaymentsList from './PaymentsList';
import UploadConfirmationReceipt from './UploadConfirmationReceipt';

function Payments() {
  const [tableVers, setTableVers] = useState(0);
  const [createFormKey, setCreateFormKey] = useState(0);
  const [currentCreateId, setCurrentCreateId] = useState('');

  const handleCreateFormOnCancel = () => {
    setCurrentCreateId('');
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterSave = () => {
    setTableVers((prevTableVers) => prevTableVers + 1);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  return (
    <>
      <PaymentsList
        onUploadReceipt={(id: string) => {
          setCurrentCreateId(id);
        }}
        tableVersion={tableVers}
      />

      {currentCreateId !== '' && (
        <UploadConfirmationReceipt key={createFormKey} isOpen={!!currentCreateId} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} paymentId={currentCreateId} />
      )}
    </>
  );
}

export default Payments;
