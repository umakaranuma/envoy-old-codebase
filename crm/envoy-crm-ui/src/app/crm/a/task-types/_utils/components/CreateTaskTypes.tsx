import { useTrans } from '@/helpers/services/lang/langService';
import React, { FormEvent, useState } from 'react';
import { initFormData } from '../model';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { form } from '@/constans/Form';
import { createTaskTypes } from '../api-service';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input } from '@apptimus-ui/ui-element';

function CreateTaskTypes({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const t = useTrans('label.task_types,otr.common');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  const tBe = useTrans('be.msg,be.error,be.attri');
  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.task_type_crud.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createTaskTypes(formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.task_type_crud.store, tBe);
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
      <ModalHeader title={t('add_new_task_type')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.task_type_crud.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              <Input isRequired label={t('name')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 mb-3">
              <Input
                label={t('description')}
                value={formData.description}
                onChange={(e) => onFormChange('description', e.target.value)}
                className="form-control error-description"
                name="description"
                type="textarea"
              />
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('create')} type="submit" size="sm" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" size="sm" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default CreateTaskTypes;
