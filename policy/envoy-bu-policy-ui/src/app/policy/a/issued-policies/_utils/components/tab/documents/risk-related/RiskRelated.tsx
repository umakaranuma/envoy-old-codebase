import React, { useState } from 'react';
import RiskRelatedList from './RiskRelatedList';
import { useTrans } from '@/helpers/services/lang/langService';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import AddRiskDocument from './AddRiskDocument';
import EditRiskDocument from './EditRiskDocument';
import { toaster } from '@/helpers/services/toaster';
import { deleteIssuedPolicyDocument } from '../../../../api-service';

function RiskRelated({ policyId }: { policyId: string }) {
  const t = useTrans('label.policy_request,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [createFormVisible, setCreateFormVisible] = useState(false);
  const [currentEditId, setCurrentEditId] = useState('');
  const [tableVers, setTableVers] = useState(0);

  const reloadTable = () => {
    setTableVers((prev) => prev + 1);
  };

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteIssuedPolicyDocument(deleteId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      onClose();
      reloadTable();
    }
  };

  return (
    <div>
      <div className="d-flex gap-2 align-items-center justify-content-end mb-4">
        <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
          <Flexicon icon="plus-circle" size={18} />
          <span className="d-none d-sm-inline">{t('add_risk_related_document')}</span>
        </Button>
      </div>
      <RiskRelatedList onEdit={(id: any) => setCurrentEditId(id)} tableVers={tableVers} handleOnDelete={handleOnDelete} policyId={policyId} />
      {createFormVisible && (
        <AddRiskDocument
          isOpen={createFormVisible}
          onCancel={() => setCreateFormVisible(false)}
          afterSave={() => {
            setCreateFormVisible(false), reloadTable();
          }}
          issuedPolicyId={policyId}
        />
      )}
      {currentEditId !== '' && (
        <EditRiskDocument
          isOpen={currentEditId !== ''}
          editId={currentEditId}
          onCancel={() => setCurrentEditId('')}
          afterSave={() => {
            setCurrentEditId(''), reloadTable();
          }}
        />
      )}
    </div>
  );
}

export default RiskRelated;
