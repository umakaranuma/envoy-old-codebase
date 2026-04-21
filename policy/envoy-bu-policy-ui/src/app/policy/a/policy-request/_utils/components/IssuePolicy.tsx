import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { IExtractResult, initIssuedPolicyFormData } from '../model';
import { addPolicyRequest, getPolicyRequestExtractedData } from '../api-service';
import InputFileUploader from '@/components/others/page-related/uploader/InputFileUploader';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import FilePreviewInput from '@/components/others/page-related/uploader/FilePreviewInput';
import { handleFileUpload } from '@/helpers/services/commonService';

function IssuePolicy({ isOpen, onCancel, afterSave, policyId }: { isOpen: boolean; onCancel: Function; afterSave: Function; policyId: string }) {
  const t = useTrans('label.policy_request,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initIssuedPolicyFormData);
  const [policyResource, setPolicyResource] = useState<File | null>(null);
  const [invoiceResource, setInvoiceResource] = useState<File | null>(null);
  const [skeleton, setSkeleton] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      setSkeleton(true);
      const responseData = await getPolicyRequestExtractedData(policyId);
      if (responseData?.is_success) {
        const data: IExtractResult = responseData.result;
        onFormChange('insurer_policy_id', data.policy_details.insurer_policy_id);
        onFormChange('insurer_invoice_id', data.invoice_details.insurer_invoice_id);
        onFormChange('policy_effective_date', data.policy_details.policy_issue_date);
        onFormChange('policy_start_date', data.policy_details.start_date);
        onFormChange('policy_expiry_date', data.policy_details.end_date);
        onFormChange('premium_amount', data.policy_details.sum_insured);
        onFormChange('credit_period_days', data.policy_details.credit_period_days);
        onFormChange('policy_document', data.policy_details.policy_document_url);
        onFormChange('policy_document_name', data.policy_details.policy_document_name);
        onFormChange('invoice_document', data.invoice_details.invoice_document_url);
        onFormChange('invoice_document_name', data.invoice_details.invoice_document_name);
      }
      setSkeleton(false);
    };

    if (policyId) {
      fetchData();
    }
  }, [policyId]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    clearError(form.policy_request.update);
    setError('');
    setIsFormProcessing(true);

    try {
      // let responseData;
      // if (issuedPolicyId) {
      //     responseData = await renewalPolicyRequest(issuedPolicyId, {
      //         ...formData,
      //         policy_document: docData?.doc,
      //         policy_document_name: docData?.name,
      //         invoice_document: invoiceFileData?.doc,
      //         invoice_document_name: invoiceFileData?.name,
      //     });
      // } else {
      const invoiceFileData = invoiceResource ? await handleFileUpload(invoiceResource, `invoice_PR${policyId}`) : null;
      const policyFileData = policyResource ? await handleFileUpload(policyResource, `policy_PR${policyId}`) : null;
      const responseData = await addPolicyRequest(policyId, {
        ...formData,
        policy_document: policyFileData?.key,
        policy_document_name: policyFileData?.name,
        invoice_document: invoiceFileData?.key,
        invoice_document_name: invoiceFileData?.name,
      });
      // }

      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.policy_request.update, tBe);
      }

      if (responseData.system_code === 'VALIDATION_ERROR') {
        setError(responseData.message);
        return;
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        afterSave();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  useEffect(() => {
    console.log('formData', formData);
  }, [formData]);

  return (
    <Modal isOpen={isOpen} size="lg" onBackdrop={() => onCancel()}>
      <ModalHeader title={t('create_policy')} onClose={() => onCancel()} />
      <ModalBody>
        <form id={`${form.policy_request.update}`}>
          <div className="row">
            <div className="col-12 col-md-4 mb-3">
              <Label htmlFor="insurer_policy_id" label={t('insurer_policy_id')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.insurer_policy_id || ''}
                  onChange={(e) => onFormChange('insurer_policy_id', e.target.value)}
                  className="form-control error-insurer_policy_id"
                  id="insurer_policy_id"
                  name="insurer_policy_id"
                />
              )}
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Label htmlFor="insurer_invoice_iD" label={t('insurer_invoice_iD')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.insurer_invoice_id || ''}
                  onChange={(e) => onFormChange('insurer_invoice_id', e.target.value)}
                  className="form-control error-insurer_invoice_id"
                  id="insurer_invoice_id"
                  name="insurer_invoice_id"
                />
              )}
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Label htmlFor="debit_note" label={t('debit_note')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <>
                  {!(formData.invoice_document_name || invoiceResource) ? (
                    <InputFileUploader data={(file: File) => setInvoiceResource(file)} className="form-control error-invoice_document" name="invoice_document" />
                  ) : (
                    <FilePreviewInput
                      fileName={invoiceResource?.name || formData.invoice_document_name}
                      onCancel={() => {
                        setInvoiceResource(null);
                        onFormChange('invoice_document_name', '');
                      }}
                    />
                  )}
                </>
              )}
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Label htmlFor="policy_document" label={t('policy_document')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <>
                  {!(formData.policy_document_name || policyResource) ? (
                    <InputFileUploader data={(file: File) => setPolicyResource(file)} className="form-control error-policy_document" name="policy_document" />
                  ) : (
                    <FilePreviewInput
                      fileName={policyResource?.name || formData.policy_document_name}
                      onCancel={() => {
                        setPolicyResource(null);
                        onFormChange('policy_document_name', '');
                      }}
                    />
                  )}
                </>
              )}
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Label htmlFor="policy_issue_date" label={t('policy_issue_date')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.policy_effective_date || ''}
                  onChange={(e) => onFormChange('policy_effective_date', e.target.value)}
                  className="form-control error-policy_effective_date"
                  id="policy_effective_date"
                  name="policy_effective_date"
                  type="date"
                />
              )}
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Label htmlFor="start_date" label={t('start_date')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.policy_start_date || ''}
                  onChange={(e) => onFormChange('policy_start_date', e.target.value)}
                  className="form-control error-policy_start_date"
                  id="policy_start_date"
                  name="policy_start_date"
                  type="date"
                />
              )}
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Label htmlFor="end_date" label={t('end_date')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.policy_expiry_date || ''}
                  onChange={(e) => onFormChange('policy_expiry_date', e.target.value)}
                  className="form-control error-policy_expiry_date"
                  id="policy_expiry_date"
                  name="policy_expiry_date"
                  type="date"
                  min={formData.policy_start_date ? new Date(formData.policy_start_date).toISOString().split('T')[0] : undefined}
                />
              )}
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Label htmlFor="premium_amount" label={t('premium_amount')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.premium_amount || ''}
                  onChange={(e) => onFormChange('premium_amount', parseFloat(e.target.value))}
                  className="form-control error-premium_amount"
                  id="premium_amount"
                  name="premium_amount"
                />
              )}
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Label htmlFor="credit_period" label={t('credit_period')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.credit_period_days || ''}
                  onChange={(e) => onFormChange('credit_period_days', e.target.value)}
                  className="form-control error-credit_period_days"
                  id="credit_period_days"
                  name="credit_period_days"
                />
              )}
            </div>
            {error && <span className="err-msg">{tBe(error)}</span>}
          </div>
        </form>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('submit')} onClick={onSubmit} width="sm" isLoading={isFormProcessing} />
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default IssuePolicy;
