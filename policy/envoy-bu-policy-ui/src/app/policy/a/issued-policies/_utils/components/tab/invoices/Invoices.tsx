'use client';
import React, { useState } from 'react';
import InvoicesList from './InvoicesList';
import CreatePayment from './CreatePayment';

function Invoices() {
  const [tableVers, setTableVers] = useState(0);
  const [createFormKey, setCreateFormKey] = useState(0);
  const [createFormVisible, setCreateFormVisible] = useState(false);
  const [currentViewId, setCurrentViewId] = useState('');

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
      <InvoicesList
        onView={(id: string) => {
          setCurrentViewId(id);
          setCreateFormVisible(true);
        }}
        tableVers={tableVers}
      />

      {currentViewId !== '' && <CreatePayment key={createFormKey} isOpen={createFormVisible} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} invoiceId={currentViewId} />}
    </>
  );
}

export default Invoices;
