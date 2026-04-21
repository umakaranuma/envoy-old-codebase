'use client';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import React, { useState } from 'react';
import QuotationList from './QuotationList';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import CreateRequest from './create/CreateRequest';
import { useRouter } from 'next/navigation';
import { getDefaultEmailTemplateForInsurer } from '../service';
import { toaster } from '@/helpers/services/toaster';
import { revertQuotation, sendApproval } from '../api-service';
import EmailForm from '@/components/others/page-related/email-form/EmailForm';

function Quotations({ leadIdFromCrm = '', afterCreateRequest, isHideCreate = false }: { leadIdFromCrm?: string; afterCreateRequest?: Function; isHideCreate?: boolean }) {
  const t = useTrans('label.quotations,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [tableVers, setTableVers] = useState(0);
  const [createFormKey, setCreateFormKey] = useState(0);
  const [createFormVisible, setCreateFormVisible] = useState(false);
  const [emailFormKey, setEmailFormKey] = useState(0);
  const router = useRouter();
  const [submissionData, setSubmissionData] = useState<{ id: string; data: any; recipients: { id: string; name: string }[] } | null>(null);
  const [isFormProcessing, setIsFormProcessing] = useState(false);

  const handleCreateFormOnCancel = () => {
    setCreateFormVisible(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleCloseEmailForm = () => {
    setSubmissionData(null);
    setTableVers((prevTableVers) => prevTableVers + 1);
    setEmailFormKey((prevFormKey) => prevFormKey + 1);
  };

  const handleSentApproval = async (data: any) => {
    try {
      // const uploadedFiles = data.files ? data.files.map((file: any) => ({ doc:file.doc_link, name: file.doc_name, type: file.doc_type })) : [];
      // const coverageLinks = data.defaultDocuments.map((cov: any) => ({ doc: cov.coverage_details, name: cov.coverage_details_name }));
      // const mergedArray = uploadedFiles.concat(coverageLinks);
      setIsFormProcessing(true);
      const responseData = await sendApproval({
        entity_type: 'common_approval',
        action: 'approval',
        entity_data: { id: submissionData?.id },
        // service_provider_ids: recipients.map((sp) => sp.id),
        // documents: mergedArray,
        email_data: data,
      });

      if (responseData.is_success) {
        handleCloseEmailForm();
        if (afterCreateRequest) {
          afterCreateRequest();
        }
        setIsFormProcessing(false);
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  };

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function) => {
    setLoader(true);
    const responseData = await revertQuotation(deleteId);
    setLoader(false);
    if (responseData.system_code === 'CONFLICT') {
      toaster.error(responseData.message);
      return;
    }
    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      setTableVers((prevValue) => prevValue + 1);
    }
  };

  return (
    <>
      <div className={`${leadIdFromCrm === '' && 'page-header-breadcrumb custom-page-header'}`}>
        {leadIdFromCrm === '' && <PageHeading title={t('quotation_management')} icon="core" />}
        <div className={`d-flex gap-2 align-items-center ${leadIdFromCrm !== '' && 'justify-content-end'}`}>
          {!isHideCreate && (
            <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
              <Flexicon icon="plus-circle" size={18} />
              <span className="d-none d-sm-inline">{t('request_quotation')}</span>
            </Button>
          )}
          {/* {leadIdFromCrm === '' && (
            <Dropdown
              trigger={
                <Button color="primary" variant="outline" className="d-flex align-items-center gap-1">
                  <Flexicon icon="dots-vertical" variant="line" size={15} />
                </Button>
              }
            >
              {(onClose: Function) => (
                <>
                  <DropdownItem onClick={() => onClose()}>
                    <div className="d-flex align-items-center gap-2">
                      <Flexicon icon="download-cloud-02" variant="line" size={14} />
                      <span>{t('export')}</span>
                    </div>
                  </DropdownItem>
                </>
              )}
            </Dropdown>
          )} */}
        </div>
      </div>

      {leadIdFromCrm === '' && <QuotationList tableVers={tableVers} onView={(id: any) => router.push(`/crm/a/quotations/${id}`)} handleOnDelete={handleOnDelete} />}
      {createFormVisible && <CreateRequest key={createFormKey} isOpen={createFormVisible} onCancel={handleCreateFormOnCancel} leadIdFromCRM={leadIdFromCrm} setSubmissionData={setSubmissionData} />}
      {submissionData?.id && (
        <EmailForm
          defaultTemplate={getDefaultEmailTemplateForInsurer()}
          key={emailFormKey}
          isOpen={submissionData.id !== ''}
          onCancel={handleCloseEmailForm}
          recipientNames={submissionData.recipients.map((sp) => sp.name)}
          emailData={(data: any) => handleSentApproval(data)}
          defaultFiles={[{ doc: submissionData.data?.file_key, name: submissionData.data?.file_name }]}
          disableRemove={true}
          isFormProcessing={isFormProcessing}
        />
      )}
      {/* {isOpenCustomerCreate && <CustomersCreate isOpen={isOpenCustomerCreate} onCancel={() => setIsOpenCustomerCreate(false)} />} */}
      {/* {isOpenCustomerCreate && <AccountsCreate isOpen={isOpenCustomerCreate} onCancel={() => setIsOpenCustomerCreate(false)} afterSave={() => {}} />} */}
    </>
  );
}

export default Quotations;
