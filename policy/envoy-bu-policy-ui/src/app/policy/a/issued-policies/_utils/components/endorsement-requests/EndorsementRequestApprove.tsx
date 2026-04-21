import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { acceptEndorsementRequest } from '../../api-service';
import { Flexicon } from '@apptimus-ui/flexicon';

function EndorsementRequestApprove({ isOpen, onCancel, approveId, afterSave, type }: { isOpen: boolean; onCancel: Function; approveId: string | null; afterSave: Function; type: string }) {
  const t = useTrans('label.issued_policies,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({ cover_value: '', endorsement_request_id: '', credit_period: '' });

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.endorsementRequests.store);
    setIsFormProcessing(true);
    try {
      const responseData = await acceptEndorsementRequest({ ...formData, endorsement_request_id: approveId, type: type === 'cancellation' ? 'cancellation' : undefined });
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.endorsementRequests.store, tBe);
      }

      if (responseData.is_success) {
        afterSave();
        setFormData({ cover_value: '', endorsement_request_id: '', credit_period: '' });
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('endorsement')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.endorsementRequests.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              <Label htmlFor="cover_values" label={type === 'cancellation' ? t('refunded_amount') : t('cover_values')} isRequired />
              <Input type="number" value={formData.cover_value} onChange={(e) => onFormChange('cover_value', e.target.value)} className="form-control error-cover_value" name="cover_value" />
            </div>
            <div className="col-12 mb-3">
              <Label htmlFor="credit_period" label={t('credit_period')} isRequired />
              <Input type="number" value={formData.credit_period} onChange={(e) => onFormChange('credit_period', e.target.value)} className="form-control error-credit_period" name="credit_period" />
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
            <Button type="submit" width="sm" isLoading={isFormProcessing}>
              <span className="d-flex gap-2">
                <Flexicon icon="check-circle" variant="line" size={17} />
                <span>{t('accept')}</span>
              </span>
            </Button>
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default EndorsementRequestApprove;
