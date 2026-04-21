'use client';
import React, { useState } from 'react';
import EndorsementRequestsList from './EndorsementRequestsList';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import EndorsementRequestsCreate from './EndorsementRequestsCreate';
import EmailForm from '../../../../../../../components/others/page-related/email-form/EmailForm';
import { IEmailData } from '../../model';
import { toaster } from '@/helpers/services/toaster';
import { sendEndorsementEmail } from '../../api-service';
import { getDefaultEmailTemplateForInsurer } from '../../service';
import EndorsementRequestApprove from './EndorsementRequestApprove';

function EndorsementRequests({
  setEndorsementDetailTableVersion,
  setInvoiceKey,
  statusType,
  afterSave,
}: {
  setEndorsementDetailTableVersion: Function;
  setInvoiceKey: Function;
  statusType: string;
  afterSave: Function;
}) {
  const tBe = useTrans('be.msg,be.error,be.attri');
  const t = useTrans('label.issued_policies,otr.common');
  const [tableVers, setTableVers] = useState(0);
  const [_currentEditId, _setCurrentEditId] = useState('');
  const [createFormKey, setCreateFormKey] = useState(0);
  const [createFormVisible, setCreateFormVisible] = useState(false);
  const [emailData, setEmailData] = useState({} as IEmailData);
  const [emailFormKey, setEmailFormKey] = useState(0);
  const [approveFormVisible, setapproveFormVisible] = useState(false);
  const [approveId, setApproveId] = useState<string | null>(null);
  const [endorsementType, setEndorsementType] = useState<string | null>(null);

  const handleCreateCoverValueFormOnCancel = () => {
    setApproveId(null);
    setapproveFormVisible(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleCreateFormOnCancel = () => {
    setCreateFormVisible(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleCloseEmailForm = () => {
    setEmailData({} as IEmailData);
    setEmailFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleSentEmail = async (data: any) => {
    try {
      // const uploadedFiles = data.files ? data.files.map((file: any) => process.env.NEXT_PUBLIC_S3CDN + '/' + file.doc_link) : [];

      const responseData = await sendEndorsementEmail({
        subject: data.subject,
        body: data.body,
        documents: data.documents,
        endorsement_request_id: emailData.id,
      });

      if (responseData.is_success) {
        handleCloseEmailForm();
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  };

  return (
    <div className="panel">
      <div className="d-flex flex-row justify-content-between align-items-center mb-3">
        <div className="panel-title">{t('endorsement_requests')}</div>
        {statusType !== 'policy_cancelled' && (
          <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('add_new')}</span>
          </Button>
        )}
      </div>

      <EndorsementRequestsList
        tableVers={tableVers}
        setEmailData={setEmailData}
        setapproveFormVisible={setapproveFormVisible}
        setApproveId={(id: string, type: string) => {
          setApproveId(id);
          setEndorsementType(type);
        }}
      />

      {createFormVisible && (
        <EndorsementRequestsCreate
          key={createFormKey}
          isOpen={createFormVisible}
          onCancel={handleCreateFormOnCancel}
          setEmailData={setEmailData}
          afterSave={() => setTableVers((prevVers) => prevVers + 1)}
        />
      )}

      {approveFormVisible && (
        <EndorsementRequestApprove
          approveId={approveId}
          key={createFormKey}
          isOpen={approveFormVisible}
          onCancel={handleCreateCoverValueFormOnCancel}
          type={endorsementType === 'Cancellations' ? 'cancellation' : 'endorsement'}
          afterSave={() => {
            setTableVers((prevVers) => prevVers + 1);
            setEndorsementDetailTableVersion((prevVers: number) => prevVers + 1);
            setInvoiceKey((prevKey: number) => prevKey + 1);
            setapproveFormVisible(false);
            afterSave();
          }}
        />
      )}

      {emailData?.id && (
        <EmailForm
          key={emailFormKey}
          isOpen={emailData.id !== ''}
          onCancel={() => setEmailData({} as IEmailData)}
          recipientNames={[emailData.insurer_name]}
          defaultTemplate={getDefaultEmailTemplateForInsurer(emailData.insurer_name, emailData.policy_holder_name, emailData.policy_id, emailData.effective_date)}
          emailData={(data: any) => handleSentEmail(data)}
        />
      )}
    </div>
  );
}

export default EndorsementRequests;
