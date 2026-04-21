'use client';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import React, { useState } from 'react';
import PaymentsList from './PaymentsList';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { toaster } from '@/helpers/services/toaster';
import { deletePayments } from '../api-service';
import PaymentsCreate from './PaymentsCreate';
import { useRouter } from 'next/navigation';

function Payments() {
  const [tableVers, setTableVers] = useState(0);
  const t = useTrans('label.payments,otr.common,be.msg');
  const [createFormKey, setCreateFormKey] = useState(0);
  const [createFormVisible, setCreateFormVisible] = useState(false);
  const [_currentViewId, setCurrentViewId] = useState('');

  const router = useRouter();
  const handleCreateFormOnCancel = () => {
    setCreateFormVisible(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterSave = () => {
    setTableVers((prevTableVers) => prevTableVers + 1);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  // const handleAfterUpdate = () => {
  //   setCurrentEditId('');
  //   setTableVers((prevTableVers) => prevTableVers + 1);
  // };

  const tBe = useTrans('be.msg,be.error,be.attri');

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deletePayments(deleteId);
    setLoader(false);

    if (responseData.status_code === 409) {
      toaster.error(tBe(responseData.message));
    }

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      onClose();
      setTableVers((prevTableVers) => prevTableVers + 1);
    }
  };

  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('payments')} icon="core" />
        <div className="d-flex gap-2">
          <Button
            className="d-flex align-items-center gap-1"
            onClick={() => {
              router.push('/finance/a/payments/upload');
            }}
            size="md"
            color="light"
          >
            {/* <Flexicon icon="upload-01" size={18} /> */}
            <Flexicon icon="download-01" variant="line" size={18} />
            <span>{t('import')}</span>
          </Button>
          <Button className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('add_new_entity', { entity: t('payment') })}</span>
          </Button>
        </div>
      </div>

      <PaymentsList tableVers={tableVers} onView={(id: string) => setCurrentViewId(id)} handleOnDelete={handleOnDelete} />

      {/* {currentViewId !== '' && <PaymentsView viewId={currentViewId} isOpen={currentViewId !== ''} onClose={() => setCurrentViewId('')} setEditId={(id: any) => setCurrentEditId(id)} />} */}

      {createFormVisible && <PaymentsCreate key={createFormKey} isOpen={createFormVisible} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} />}

      {/* {currentEditId !== '' && <PaymentsEdit editId={currentEditId} isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterUpdate={handleAfterUpdate} />} */}
    </>
  );
}

export default Payments;
