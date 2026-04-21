import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { uploadConfirmationReceipt } from '../../../api-service';
import { ImageDragAndDrop } from '@/components/others/page-related/uploader/ImageDragAndDrop';
import { handleFileUpload } from '@/helpers/services/commonService';
import FilePreviewInput from '@/components/others/page-related/uploader/FilePreviewInput';

function UploadConfirmationReceipt({ isOpen, onCancel, afterSave, paymentId }: { isOpen: boolean; onCancel: Function; afterSave: Function; paymentId: string }) {
  const t = useTrans('label.issued_policies,otr.common');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [resource, setResource] = useState<File | null>(null);

  const tBe = useTrans('be.msg,be.error,be.attri');
  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.payment_crud.store);
    setIsFormProcessing(true);

    try {
      const docData = await handleFileUpload(resource);
      const responseData = await uploadConfirmationReceipt(
        {
          confirmation_payment_receipt_url: docData?.key,
          confirmation_payment_receipt_name: docData?.name,
          confirmation_payment_receipt_type: docData?.type,
        },
        paymentId,
      );
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.payment_crud.store, tBe);
      }

      if (responseData.is_success) {
        onCancel();
        afterSave();
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('upload_confirmation_receipt')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.payment_crud.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              <Label htmlFor="upload_receipt" label={t('upload_receipt')} isRequired />
              {!resource ? (
                <ImageDragAndDrop htmlFor={'document'} selectedImage={(file: File) => setResource(file)} className="form-control error-confirmation_payment_receipt_name" />
              ) : (
                <FilePreviewInput
                  fileName={resource?.name || ''}
                  onCancel={() => {
                    setResource(null);
                  }}
                />
              )}
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('submit')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default UploadConfirmationReceipt;
