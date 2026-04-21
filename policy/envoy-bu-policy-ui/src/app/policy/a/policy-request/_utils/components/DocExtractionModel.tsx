import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Select } from '@apptimus-ui/select';
import { Button, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useEffect, useState } from 'react';
import { extractDocs } from '../api-service';
import FilePreviewer from '@/components/others/page-related/chat/_utils/components/FilePreviewer';

function DocExtractionModal({
  isOpen,
  onCancel,
  afterSave,
  policyRequestId,
  docExtractionData,
}: {
  isOpen: boolean;
  onCancel: Function;
  afterSave: Function;
  policyRequestId: string;
  docExtractionData: any | null;
}) {
  const t = useTrans('label.policy_request,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [formData, setFormData] = useState({} as any);
  const [isFormProcessing, setIsFormProcessing] = useState(false);

  function removeBaseUrl(url: string): string {
    const base = process.env.S3CDN || '';
    return url.startsWith(base) ? url.slice(base.length) : url;
  }

  useEffect(() => {
    console.log('docExtractionData', docExtractionData);
    if (docExtractionData) {
      setFormData({
        document_type: docExtractionData?.type,
        document_url: removeBaseUrl(docExtractionData?.url),
        document_name: docExtractionData?.name,
      });
    }
  }, [docExtractionData]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.chat.store);
    setIsFormProcessing(true);
    try {
      const response = await extractDocs(formData, policyRequestId);
      if (response?.status_code === 417) {
        printError(response?.result, form.chat.store, tBe);
      } else if (response?.is_success) {
        afterSave();
        setFormData({
          document_type: docExtractionData?.content_type,
          document_url: removeBaseUrl(docExtractionData?.download_url),
          document_name: docExtractionData?.file_name,
        });
        toaster.success(tBe(response?.message || ''));
      }
    } catch (error) {
      console.error('Submit error:', error);
    } finally {
      setIsFormProcessing(false);
    }
  }

  const handleCancel = () => {
    onCancel();
    setFormData({
      document_type: docExtractionData?.content_type,
      document_url: removeBaseUrl(docExtractionData?.download_url),
      document_name: docExtractionData?.file_name,
    });
    clearError(form.chat.store);
  };

  return (
    <Modal isOpen={isOpen} onBackdrop={() => handleCancel()}>
      <ModalHeader title={t('document_extraction')} onClose={() => handleCancel()} />
      <form onSubmit={onSubmit} id={`${form.chat.store}`}>
        <ModalBody>
          <div className="col-12 col-md-12 mb-3 custom-select">
            <Label htmlFor="document_type" label={t('document_type')} isRequired />
            <Select
              onChange={(value) => onFormChange('type', value)}
              options={[
                { label: t('insurer_policy'), value: 'insurer_policy' },
                { label: t('insurer_invoice'), value: 'insurer_invoice' },
                { label: t('others'), value: 'others' },
              ]}
              option={{ label: 'label', value: 'value' }}
              isSearchable={false}
              className="form-control error-type"
              defaultValue={{}}
            />
          </div>
          <div className="col-12 col-md-12 mb-3 custom-select">
            <Label htmlFor="document" label={t('document')} isRequired />
            <FilePreviewer file={docExtractionData} />
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('add')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => handleCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default DocExtractionModal;
