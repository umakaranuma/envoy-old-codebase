'use client';
import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { createProductItem } from '../api-service';

export function CreateProductItem({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const t = useTrans('label.product_item,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({ title: '', description: '' });

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    clearError(form.product_item.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createProductItem(formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.product_item.store, tBe);
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
      <ModalHeader title={t('add_new_entity', { entity: t('product_item') })} onClose={() => onCancel()} />
      <ModalBody>
        <div id={`${form.product_item.store}`} className="row">
          <div className="col-12 mb-4">
            <Input isRequired label={t('title')} value={formData.title} onChange={(e) => onFormChange('title', e.target.value)} className="form-control error-title" name="title" />
          </div>
          <div className="col-12 mb-4">
            <Input
              label={t('description')}
              type="textarea"
              value={formData.description}
              onChange={(e) => onFormChange('description', e.target.value)}
              className="form-control error-description"
              name="description"
            />
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('create')} onClick={onSubmit} width="sm" isLoading={isFormProcessing} />
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}
