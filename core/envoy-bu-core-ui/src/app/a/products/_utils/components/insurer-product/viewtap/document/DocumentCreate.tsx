import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useEffect, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { toaster } from '@/helpers/services/toaster';
import { initDocument } from '../../../../modal';
import { createInsurerProductDocument } from '../../../../api-service';

function DocumentCreate({ isOpen, onCancel, afterSave, productId, type }: { isOpen: boolean; onCancel: Function; afterSave: Function; productId: string; type: string }) {
  const t = useTrans('label.products,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initDocument);

  useEffect(() => {
    onFormChange('type', type);
  }, []);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.job_title.store);
    setIsFormProcessing(true);

    try {
      const apiData = { documents: [formData] };
      const responseData = await createInsurerProductDocument(productId, apiData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.job_title.store, tBe);
      }

      if (responseData.is_success) {
        afterSave();
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('add_new_document')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.job_title.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              <Label label={t('name')} isRequired />
              <Input type="text" value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} placeholder={t('name')} />
            </div>
            <div className="col-12 mb-3">
              <div className="form-check">
                <input type="checkbox" className="form-check-input" checked={formData.is_mandatory} onChange={(e) => onFormChange('is_mandatory', e.target.checked)} />
                <Label label={t('is_mandatory')} />
              </div>
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('create')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default DocumentCreate;
