import { useTrans } from '@/helpers/services/lang/langService';
import React, { useEffect, useState } from 'react';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import SentOutList from './SentOutList';
import DraftDocumentList from './DraftDocumentList';
import { toaster } from '@/helpers/services/toaster';
import { sendEmailToCustomer } from '../../../api-service';
import { getDefaultEmailTemplateForCustomer } from '../../../service';
import { UploadDocument } from './UploadDocument';
import EditGeneratedDocument from './EditGeneratedDocument';
import { fileReceiver } from '@/helpers/services/storageService';
import { IEmailData } from '../../../model';
import EmailForm from '@/components/others/page-related/email-form/EmailForm';

function RecommendationDocumentation({ quotationId }: { quotationId: string }) {
  const t = useTrans('label.quotations,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [tableVers, setTableVers] = useState(0);
  const [tab, setTab] = useState('sent_out');
  const [createFormVisible, setCreateFormVisible] = useState(false);
  const [createFormKey, setCreateFormKey] = useState(0);
  const [currentEditId, setCurrentEditId] = useState('');
  const [emailData, setEmailData] = useState({} as IEmailData);
  const [emailFormKey, setEmailFormKey] = useState(0);
  const [emailDataForManualDocument, setEmailDataForManualDocument] = useState({} as IEmailData);
  const [isLoading, setIsLoading] = useState(false);
  const [isFormProcessing, setIsFormProcessing] = useState(false);

  useEffect(() => {
    toggleTableTab('sent_out');
  }, []);

  const toggleTableTab = (activeTab: string) => {
    setTab(activeTab);
    // router.push(`/crm/a/quotations/${quotationId}?t=${activeTab}`);
  };

  const handleCreateFormOnCancel = () => {
    setCreateFormVisible(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleCloseEmailForm = () => {
    setEmailData({} as IEmailData);
    setEmailFormKey((prevFormKey) => prevFormKey + 1);
  };

  const handleCloseManualEmailForm = () => {
    setEmailDataForManualDocument({} as IEmailData);
    setEmailFormKey((prevFormKey) => prevFormKey + 1);
  };

  const handleSentEmail = async (data: any) => {
    try {
      // const uploadedFiles = data.files ? data.files.map((file: any) => process.env.NEXT_PUBLIC_S3CDN + '/' + file.doc_link) : [];
      // const coverageLinks = data.defaultDocuments.map((cov: any) => cov.coverage_details);
      // const mergedArray = uploadedFiles.concat(coverageLinks);
      setIsLoading(true);
      const responseData = await sendEmailToCustomer({
        customer_id: emailData.id,
        subject: data.subject,
        body: data.body,
        documents: data.documents,
        send_quotation_id: emailData.send_quotation_id,
      });

      if (responseData.is_success) {
        handleCloseEmailForm();
        toaster.success(tBe(responseData.message));
      }
      //setIsLoading(false)
    } catch (error) {
      console.error('An error occurred:', error);
    }
  };

  const handleSentManualEmail = async (data: any) => {
    try {
      // const uploadedFiles = data.files ? data.files.map((file: any) => process.env.NEXT_PUBLIC_S3CDN + '/' + file.doc_link) : [];
      // const coverageLinks = data.defaultDocuments.map((cov: any) => process.env.NEXT_PUBLIC_S3CDN + '/' + cov.coverage_details);
      // const mergedArray = uploadedFiles.concat(coverageLinks);
      setIsFormProcessing(true);
      const responseData = await sendEmailToCustomer({
        customer_id: emailDataForManualDocument.id,
        subject: data.subject,
        body: data.body,
        documents: data.documents,
        send_quotation_id: emailDataForManualDocument.send_quotation_id,
      });

      if (responseData.is_success) {
        handleCloseManualEmailForm();
        setTableVers((prevTableVers) => prevTableVers + 1);
        toaster.success(tBe(responseData.message));
      }
      setIsFormProcessing(false);
    } catch (error) {
      console.error('An error occurred:', error);
    }
  };

  const handleAfterSave = () => {
    setTableVers((prevTableVers) => prevTableVers + 1);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const viewFile = async (key: string) => {
    try {
      const fileUrl = await fileReceiver({ key });
      window.open(fileUrl, '_blank');
    } catch (error) {
      console.error('Error opening file:', error);
    }
  };

  return (
    <>
      <div>
        <div className="tap-btn-container my-3">
          <div className="il-tab ms-2">
            <div className={`il-tab-item ${tab === 'sent_out' ? 'active' : ''}`} onClick={() => toggleTableTab('sent_out')}>
              {t('sent_out')}
            </div>
            <div className={`il-tab-item ${tab === 'draft_document' ? 'active' : ''}`} onClick={() => toggleTableTab('draft_document')}>
              {t('document')}
            </div>
          </div>
          {tab === 'draft_document' && (
            <Button className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
              <Flexicon icon="plus-circle" size={18} />
              <span className="d-none d-sm-inline">{t('upload_document')}</span>
            </Button>
          )}
        </div>
        {/* <div className="fs-15 fw-semibold mb-4">{t('recommendation_documents')}</div> */}
        <div>{tab === 'sent_out' && <SentOutList quotationId={quotationId} />}</div>
        {tab === 'draft_document' && (
          <DraftDocumentList
            quotationId={quotationId}
            onEdit={(id: any) => setCurrentEditId(id)}
            tableVers={tableVers}
            onSend={(data: IEmailData) => setEmailDataForManualDocument(data)}
            onView={(key: string) => viewFile(key)}
          />
        )}
      </div>
      {currentEditId !== '' && (
        <EditGeneratedDocument
          quotationId={quotationId}
          isOpen={currentEditId !== ''}
          currentEditId={currentEditId}
          onCancel={() => setCurrentEditId('')}
          setEmailData={setEmailData}
          afterSave={() => {
            setCurrentEditId(''), setTableVers((prevTableVers) => prevTableVers + 1);
          }}
        />
      )}
      {createFormVisible && <UploadDocument key={createFormKey} isOpen={createFormVisible} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} quotationId={quotationId} />}
      {emailData?.id && (
        <EmailForm
          key={emailFormKey}
          isOpen={emailData.id !== ''}
          onCancel={() => setEmailData({} as IEmailData)}
          recipientNames={[emailData.name]}
          defaultTemplate={getDefaultEmailTemplateForCustomer(emailData.name)}
          emailData={(data: any) => handleSentEmail(data)}
          defaultFiles={emailData.documents}
          isFormProcessing={isLoading}
        />
      )}
      {emailDataForManualDocument?.id && (
        <EmailForm
          key={emailFormKey}
          isOpen={emailDataForManualDocument.id !== ''}
          onCancel={() => setEmailDataForManualDocument({} as IEmailData)}
          recipientNames={[emailDataForManualDocument.name]}
          defaultTemplate={getDefaultEmailTemplateForCustomer(emailDataForManualDocument.name)}
          emailData={(data: any) => handleSentManualEmail(data)}
          defaultFiles={emailDataForManualDocument.documents}
          isFormProcessing={isFormProcessing}
        />
      )}
    </>
  );
}

export default RecommendationDocumentation;
