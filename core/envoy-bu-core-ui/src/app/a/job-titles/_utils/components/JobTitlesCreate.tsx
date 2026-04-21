import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { initFormData } from '../model';
import { createJobtitle } from '../api-service';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { toaster } from '@/helpers/services/toaster';

function JobTitlesCreate({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const t = useTrans('label.job_titles,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.job_title.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createJobtitle(formData);
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
    <Modal isOpen={isOpen} onBackdrop={() => onCancel()}>
      <ModalHeader title={t('add_new_job_title', { entity: t('job_title') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.job_title.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              <Input isRequired label={t('title')} value={formData.title} onChange={(e) => onFormChange('title', e.target.value)} className="form-control error-title" name="title" />
            </div>
            <div className="col-12 mb-3">
              <Input
                label={t('description')}
                value={formData.description}
                onChange={(e) => onFormChange('description', e.target.value)}
                className="form-control error-description"
                name="description"
                type="textarea"
                rows={4}
              />
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

export default JobTitlesCreate;
