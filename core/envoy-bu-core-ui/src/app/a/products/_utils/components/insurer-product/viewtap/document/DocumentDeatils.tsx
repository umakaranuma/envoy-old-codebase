import React, { useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import DocumentList from './DocumentList';
import DocumentCreate from './DocumentCreate';
import { DocumentEdit } from './DocumentEdit';
import { toaster } from '@/helpers/services/toaster';
import { IDocument } from '../../../../modal';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { deleteInsurerProductDocument } from '../../../../api-service';

function DocumentDeatils({ viewId, isView = true }: { viewId: string; isView: boolean }) {
  const t = useTrans('label.products,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [activetab, setActiveTab] = useState('policy-related');
  const [currentEditData, setCurrentEditData] = useState<IDocument | null>(null);
  const [tableVers, setTableVers] = useState(0);
  const [createFormKey, setCreateFormKey] = useState(0);
  const [createFormVisible, setCreateFormVisible] = useState(false);

  const handleAfterUpdate = () => {
    setCurrentEditData(null);
    setTableVers((prevTableVers) => prevTableVers + 1);
  };

  const handleCreateFormOnCancel = () => {
    setCreateFormVisible(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterSave = () => {
    setTableVers((prevTableVers) => prevTableVers + 1);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteInsurerProductDocument(deleteId);
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
      <div className="il-tab mt-3 ms-3">
        <div
          className={`il-tab-item ${activetab === 'policy-related' ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('policy-related');
          }}
        >
          {t('policy_relateds')}
        </div>
        <div
          className={`il-tab-item ${activetab === 'risk-related' ? 'active' : ''}`}
          onClick={() => {
            setActiveTab('risk-related');
          }}
        >
          {t('risk_relateds')}
        </div>
      </div>

      {!isView && (
        <div className="d-flex justify-content-end">
          <Button className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('add_new_document')}</span>
          </Button>
        </div>
      )}

      {activetab === 'policy-related' && <DocumentList viewId={viewId} type={'policy'} isView={isView} handleOnDelete={handleOnDelete} setCurrentEditData={setCurrentEditData} tableVers={tableVers} />}
      {activetab === 'risk-related' && <DocumentList viewId={viewId} type={'risk'} isView={isView} handleOnDelete={handleOnDelete} setCurrentEditData={setCurrentEditData} tableVers={tableVers} />}

      {createFormVisible && (
        <DocumentCreate
          key={createFormKey}
          isOpen={createFormVisible}
          onCancel={handleCreateFormOnCancel}
          afterSave={handleAfterSave}
          productId={viewId}
          type={activetab === 'policy-related' ? 'policy' : 'risk'}
        />
      )}
      {currentEditData !== null && <DocumentEdit currentEditData={currentEditData} isOpen={currentEditData !== null} onCancel={() => setCurrentEditData(null)} afterUpdate={handleAfterUpdate} />}
    </>
  );
}

export default DocumentDeatils;
