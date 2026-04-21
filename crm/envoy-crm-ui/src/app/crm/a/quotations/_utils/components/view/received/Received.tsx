import { useTrans } from '@/helpers/services/lang/langService';
import React, { useEffect, useState } from 'react';
import ReceivedList from './ReceivedList';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import AddQuotation from './AddQuotation';
import EditQuotation from './EditQuotation';
import CompareQuotations from './CompareQuotations';
import ShortListedList from './shortlisted/ShortListedList';
import GenerateDocument from './shortlisted/GenerateDocument';
import Preview from './shortlisted/Preview';
import { getDefaultEmailTemplateForCustomer, getDefaultPolicyRequestEmailTemplateForInsurer } from '../../../service';
import { deleteReceivedQuotation, sendEmailToCustomer } from '../../../api-service';
import { toaster } from '@/helpers/services/toaster';
import { IEmailData } from '../../../model';
import EmailForm from '@/components/others/page-related/email-form/EmailForm';
import CreatePolicyRequest from './policy-request/CreatePolicyRequest';
import { policyRequestEmail } from '../../../policy-api-service';

function Received({ quotationId, customerId, leadId }: { quotationId: string; customerId?: number | null; leadId?: string | null }) {
  const t = useTrans('label.quotations,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [tableVers, setTableVers] = useState(0);
  const [tab, setTab] = useState('received');
  const [createFormVisible, setCreateFormVisible] = useState(false);
  const [createFormKey, setCreateFormKey] = useState(0);
  const [currentEditId, setCurrentEditId] = useState('');
  const [isCompareOpen, setIsCompareOpen] = useState(false);
  const [selectedQuotationsForGenerate, setSelectedQuotationsForGenerate] = useState([]);
  const [isGenerateOpen, setIsGenerateOpen] = useState(false);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [emailData, setEmailData] = useState({} as IEmailData);
  const [shortListTableVers, setShortListTableVers] = useState(0);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  const [previewData, _setPreviewData] = useState<any>();
  const [emailFormKey, setEmailFormKey] = useState(0);
  const [currentPolicyRequestId, setCurrentPolicyRequestId] = useState({ id: '', insurerProductId: '', insurerProductName: '', serviceProviderId: '', nativeProductId: '' });
  const [policyRequestEmailData, setPolicyRequestEmailData] = useState({ entity_id: '', policy_request_id: '', insurer: '', documents: [] as any[] });
  const [isFormProcessing, setIsFormProcessing] = useState(false);

  useEffect(() => {
    toggleTableTab('received');
  }, []);

  const toggleTableTab = (activeTab: string) => {
    setTab(activeTab);
    // router.push(`/crm/a/quotations/${quotationId}?t=${activeTab}`);
  };

  const handleCreateFormOnCancel = () => {
    setCreateFormVisible(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterSave = () => {
    setTableVers((prevTableVers) => prevTableVers + 1);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleCloseEmailForm = () => {
    setEmailData({} as IEmailData);
    setEmailFormKey((prevFormKey) => prevFormKey + 1);
  };

  const handleSentPolicyRequestEmail = async (data: any) => {
    try {
      // const uploadedFiles = data.files ? data.files.map((file: any) => process.env.NEXT_PUBLIC_S3CDN + '/' + file.doc_link) : [];
      setIsFormProcessing(true);
      const responseData = await policyRequestEmail({
        entity_type: 'common_approval',
        action: 'approval',
        entity_data: {
          id: policyRequestEmailData.entity_id,
        },
        email_data: data,
      });

      if (responseData.is_success) {
        setPolicyRequestEmailData({ entity_id: '', policy_request_id: '', insurer: '', documents: [] });
        toaster.success(tBe(responseData.message));
        setTableVers((prevTableVers) => prevTableVers + 1);
      }
      setIsFormProcessing(false);
    } catch (error) {
      console.error('An error occurred:', error);
    }
  };

  const handleSentEmail = async (data: any) => {
    try {
      // const uploadedFiles = data.files ? data.files.map((file: any) => process.env.NEXT_PUBLIC_S3CDN + '/' + file.doc_link) : [];
      // const coverageLinks = data.defaultDocuments.map((cov: any) => cov.coverage_details);
      // const mergedArray = uploadedFiles.concat(coverageLinks);
      setIsFormProcessing(true);
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
      setIsFormProcessing(false);
    } catch (error) {
      console.error('An error occurred:', error);
    }
  };

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteReceivedQuotation(deleteId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      onClose();
      setTableVers((prevTableVers) => prevTableVers + 1);
    }
  };

  useEffect(() => {
    console.log('emailData', emailData);
  }, [emailData]);

  return (
    <>
      <div className="tap-btn-container my-3">
        <div className="il-tab ms-2">
          <div className={`il-tab-item ${tab === 'received' ? 'active' : ''}`} onClick={() => toggleTableTab('received')}>
            {t('received')}
          </div>
          <div className={`il-tab-item ${tab === 'shortlisted' ? 'active' : ''}`} onClick={() => toggleTableTab('shortlisted')}>
            {t('shortlisted')}
          </div>
        </div>
        <div className="d-flex gap-2 align-items-center justify-content-end">
          {tab === 'received' && (
            <>
              {selectedIds.length > 1 && (
                <Button color="light" className="d-flex align-items-center text-primary gap-1" onClick={() => setIsCompareOpen(true)}>
                  <CompareIcon />
                  <span className="d-none d-sm-inline">{t('compare_quotation')}</span>
                </Button>
              )}
              <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
                <Flexicon icon="plus-circle" size={18} />
                <span className="d-none d-sm-inline">{t('add_new')}</span>
              </Button>
            </>
          )}
          {tab === 'shortlisted' && (
            <>
              {selectedQuotationsForGenerate.length > 0 && (
                <Button color="light" className="d-flex align-items-center text-primary gap-1" onClick={() => setIsGenerateOpen(true)}>
                  <Flexicon icon="plus-circle" size={18} />
                  <span className="d-none d-sm-inline">{t('generate_recommendation_document')}</span>
                </Button>
              )}
            </>
          )}
        </div>
        {/* <div className="fs-15 fw-semibold mb-4">{t('quotation_list')}</div> */}
      </div>
      {tab === 'received' && (
        <ReceivedList
          onEdit={(id: any) => setCurrentEditId(id)}
          tableVers={tableVers}
          selectedIds={(ids: any) => setSelectedIds(ids)}
          handleOnDelete={handleOnDelete}
          quotationId={quotationId}
          onPolicyRequest={(id: any, insurerProductId: any, insurerProductName: any, serviceProviderId: any, nativeProductId: any) =>
            setCurrentPolicyRequestId({ id, insurerProductId, insurerProductName, serviceProviderId, nativeProductId })
          }
          setShareData={(data: any) => setEmailData({ id: data.id, name: data.name, documents: data.documents, send_quotation_id: quotationId })}
        />
      )}
      {tab === 'shortlisted' && <ShortListedList tableVers={shortListTableVers} selectedIds={(id: any) => setSelectedQuotationsForGenerate(id)} quotationId={quotationId} />}

      {createFormVisible && <AddQuotation key={createFormKey} isOpen={createFormVisible} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} quotationId={quotationId} />}
      {currentEditId !== '' && (
        <EditQuotation
          isOpen={currentEditId !== ''}
          onCancel={() => setCurrentEditId('')}
          editId={currentEditId}
          afterUpdate={() => {
            setTableVers((prevVers) => prevVers + 1);
          }}
        />
      )}
      {isCompareOpen && (
        <CompareQuotations isOpen={isCompareOpen} onCancel={() => setIsCompareOpen(false)} selectedIds={selectedIds} onSubmit={() => toggleTableTab('shortlisted')} quotationId={quotationId} />
      )}
      {isGenerateOpen && selectedQuotationsForGenerate.length > 0 && (
        <GenerateDocument
          selectedDocs={selectedQuotationsForGenerate}
          isOpen={isGenerateOpen}
          onCancel={() => setIsGenerateOpen(false)}
          setEmailData={setEmailData}
          afterSave={() => {
            setIsGenerateOpen(false), setShortListTableVers((prevVers) => prevVers + 1);
          }}
          quotationId={quotationId}
        />
      )}
      {isPreviewOpen && <Preview isOpen={isPreviewOpen} setIsPreviewOpen={setIsPreviewOpen} previewData={previewData} />}
      {emailData?.id && (
        <EmailForm
          key={emailFormKey}
          isOpen={emailData.id !== ''}
          onCancel={() => setEmailData({} as IEmailData)}
          recipientNames={[emailData.name]}
          defaultFiles={emailData.documents}
          defaultTemplate={getDefaultEmailTemplateForCustomer(emailData.name)}
          emailData={(data: any) => handleSentEmail(data)}
          isFormProcessing={isFormProcessing}
        />
      )}
      {currentPolicyRequestId.id !== '' && (
        <CreatePolicyRequest
          isOpen={currentPolicyRequestId.id !== ''}
          onCancel={() => setCurrentPolicyRequestId({ id: '', insurerProductId: '', insurerProductName: '', serviceProviderId: '', nativeProductId: '' })}
          setEmailData={setPolicyRequestEmailData}
          quotationId={currentPolicyRequestId.id}
          insurerProductId={currentPolicyRequestId.insurerProductId}
          insurerProductName={currentPolicyRequestId.insurerProductName}
          serviceProviderId={currentPolicyRequestId.serviceProviderId}
          cusId={customerId ? customerId : null}
          leadId={leadId ? leadId : null}
          nativeProductId={currentPolicyRequestId.nativeProductId}
        />
      )}
      {policyRequestEmailData?.entity_id && (
        <EmailForm
          isOpen={policyRequestEmailData.entity_id !== ''}
          onCancel={() => {
            setPolicyRequestEmailData({ entity_id: '', policy_request_id: '', insurer: '', documents: [] });
          }}
          recipientNames={[policyRequestEmailData.insurer]}
          defaultTemplate={getDefaultPolicyRequestEmailTemplateForInsurer(policyRequestEmailData.insurer, policyRequestEmailData.policy_request_id)}
          emailData={(data: any) => handleSentPolicyRequestEmail(data)}
          defaultFiles={policyRequestEmailData.documents}
          isFormProcessing={isFormProcessing}
        />
      )}
    </>
  );
}

export default Received;

const CompareIcon = () => (
  <svg width="18" height="18" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
    <g clipPath="url(#clip0_4600_13997)">
      <path d="M5 4.99935L6.66667 3.33268L5 1.66602" stroke="#09729A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M1.6665 6.66732C1.6665 4.82637 3.15889 3.33398 4.99984 3.33398H6.6665" stroke="#09729A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M15.0002 15L13.3335 16.6667L15.0002 18.3333" stroke="#09729A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M18.3335 13.334C18.3335 15.1749 16.8411 16.6673 15.0002 16.6673H13.3335" stroke="#09729A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      <path
        d="M6.6665 18.334C9.42793 18.334 11.6665 16.0954 11.6665 13.334C11.6665 10.5726 9.42793 8.33398 6.6665 8.33398C3.90508 8.33398 1.6665 10.5726 1.6665 13.334C1.6665 16.0954 3.90508 18.334 6.6665 18.334Z"
        stroke="#09729A"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M8.49072 5.41602C9.04578 3.25948 11.0034 1.66602 13.3332 1.66602C16.0946 1.66602 18.3332 3.90459 18.3332 6.66602C18.3332 8.9958 16.7398 10.9534 14.5833 11.5085"
        stroke="#09729A"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </g>
    <defs>
      <clipPath id="clip0_4600_13997">
        <rect width="20" height="20" fill="white" />
      </clipPath>
    </defs>
  </svg>
);
