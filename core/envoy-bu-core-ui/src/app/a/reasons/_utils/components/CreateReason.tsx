import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { initFormData } from '../model';
import { createReason } from '../api-service';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllEndorsementTypes } from '../services';

function CreateReason({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const t = useTrans('label.reason,otr.common');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  const tBe = useTrans('be.msg,be.error,be.attri');
  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.reasons_crud.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createReason(formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.reasons_crud.store, tBe);
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
      <ModalHeader title={t('add_new_reason')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.reasons_crud.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3 custom-select">
              <Label label={t('reason_type')} isRequired />
              <AsyncSelect
                onChange={(value) => onFormChange('type_id', value)}
                className="form-control error-type_id"
                option={{ label: 'name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllEndorsementTypes(searchValue, currentPage)}
              />
            </div>
            <div className="col-12 mb-3">
              <Input
                label={t('reason')}
                value={formData.reason}
                onChange={(e) => onFormChange('reason', e.target.value)}
                className="form-control error-reason"
                name="reason"
                type="textarea"
                isRequired
              />
            </div>
            <div className="mb-3">
              <input type="checkbox" checked={formData.allows_custom_reason} onChange={(e) => onFormChange('allows_custom_reason', e.target.checked ? true : false)} />
              <span className="ms-2 fs-14">{t('allow_custom_reason')}</span>
            </div>
            <div className="col-12 mb-3">
              <Input
                label={t('description')}
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
            <Button text={t('create')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default CreateReason;
