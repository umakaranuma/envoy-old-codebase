import { ImageDragAndDrop } from '@/components/others/page-related/ImageDragAndDrop';
import UploadedFile from '@/components/others/page-related/UploadedFile';
import { form } from '@/constans/Form';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Label } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';

function UploadDocument({ isOpen, onCancel, setFile }: { isOpen: boolean; onCancel: Function; setFile: Function }) {
  const t = useTrans('label.my_policy,otr.common,be.msg');
  const [isFormProcessing, _setIsFormProcessing] = useState(false);
  const [template, setTemplate] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  async function onSubmit() {
    setFile(template);
    onCancel();
    // clearError(form.settlement.store);
    //setIsFormProcessing(true);
    // try {
    //   const responseData = await CreateEndorsementRequests({ ...formData, issued_policy_id: policyId });
    //   setIsFormProcessing(false);

    //   if (responseData.status_code === 417) {
    //     printError(responseData.result, form.settlement.store, tBe);
    //   }

    //   if (responseData.is_success) {
    //     afterSave();
    //     setFormData(initEndorsementCreate);
    //     handleOpenEmail(responseData.result);
    //     toaster.success(tBe(responseData.message));
    //   }
    // } catch (error) {
    //   console.error('An error occurred:', error);
    // }
  }

  function handleSetFile(file: File) {
    setError(null);
    if (file.type !== 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' && file.type !== 'application/vnd.ms-excel') {
      setError('Unsupported file type. Please upload an Excel file.');
      return;
    }
    setTemplate(file);
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('upload_your_completed_templates')} onClose={() => onCancel()} />
      <ModalBody>
        <div id={`${form.settlement.store}`}>
          <div className="row">
            <div className="col-12 mb-3">
              <Label label={t('upload_template')} isRequired />
              {!template ? (
                <ImageDragAndDrop htmlFor={'upload_template'} fileType="excel" selectedImage={(file: File) => handleSetFile(file)} />
              ) : (
                <UploadedFile fileName={template.name} fileSize={`${(template.size / 1024).toFixed(2)} KB`} fileType={'excel'} onRemove={() => setTemplate(null)} />
              )}
            </div>
          </div>
          <span style={{ color: 'red' }} className="fs-14">
            {error}
          </span>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          <Button text={t('submit')} type="submit" width="sm" isLoading={isFormProcessing} onClick={onSubmit} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default UploadDocument;
