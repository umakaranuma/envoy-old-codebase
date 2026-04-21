import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { sendApproval } from '../api-service';

function ApprovalConfirmation({ isOpen, onCancel, afterSave, currentId, status }: { isOpen: boolean; onCancel: Function; afterSave: Function; currentId: string; status: string }) {
  const t = useTrans('label.approvals,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({ remarks: '' });

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.approvals.store);
    setIsFormProcessing(true);
    try {
      const responseData = await sendApproval(currentId, { ...formData, status });
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.approvals.store, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        afterSave();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={status === 'approved' ? t('confirmation') : t('reject')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.approvals.store}`}>
        <ModalBody>
          <div className="row">
            <div>
              <Input
                rows={3}
                type="textarea"
                isRequired
                label={t('remarks')}
                value={formData.remarks}
                onChange={(e) => onFormChange('remarks', e.target.value)}
                className="form-control error-remarks"
                name="remarks"
              />
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('confirm')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default ApprovalConfirmation;
