import React, { useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import DocumentList from './DocumentList';

function DocumentDeatils({ viewId }: { viewId: string }) {
  const t = useTrans('label.products,otr.common');
  const [activetab, setActiveTab] = useState('policy-related');

  return (
    <>
      <div className="il-tab ms-3">
        <div
          className={`il-tab-item ${activetab === 'policy-related' ? 'active shadow-sm' : ''}`}
          onClick={() => {
            setActiveTab('policy-related');
          }}
        >
          {t('policy_relateds')}
        </div>
        <div
          className={`il-tab-item ${activetab === 'risk-related' ? 'active shadow-sm' : ''}`}
          onClick={() => {
            setActiveTab('risk-related');
          }}
        >
          {t('risk_relateds')}
        </div>
      </div>
      {activetab === 'policy-related' && <DocumentList viewId={viewId} type={'policy'} />}
      {activetab === 'risk-related' && <DocumentList viewId={viewId} type={'risk'} />}
    </>
  );
}

export default DocumentDeatils;
