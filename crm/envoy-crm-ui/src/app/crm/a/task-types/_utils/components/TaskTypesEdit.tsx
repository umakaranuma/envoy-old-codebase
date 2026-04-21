import { useTrans } from '@/helpers/services/lang/langService';
import React, { FormEvent, useEffect, useState } from 'react';
import { initFormData, ITaskTypes } from '../model';
import { getOneTaskTypes, updateTaskTypes } from '../api-service';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { InputSkeleton } from '@/components/others/InputSkeleton';

export const TaskTypesEdit = ({ isOpen, editId, afterUpdate, onCancel }: { isOpen: boolean; editId: string; onCancel: Function; afterUpdate: Function }) => {
  const t = useTrans('label.task_types,otr.common');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);
  const [skeleton, setSkeleton] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneTaskTypes(editId);

      if (responseData?.is_success) {
        const data: ITaskTypes = responseData.result;
        onFormChange('name', data.name);
        onFormChange('description', data.description);
        setSkeleton(false);
      }
    };

    if (editId) {
      setSkeleton(true);
      fetchData();
    }
  }, [editId]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  const tBe = useTrans('be.msg,be.error,be.attri');
  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.task_type_crud.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updateTaskTypes(editId, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.task_type_crud.update, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setFormData(initFormData);
        afterUpdate();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('edit_task_types')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.task_type_crud.update}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              <Label htmlFor="name" label={t('name')} isRequired />
              {skeleton ? <InputSkeleton /> : <Input value={formData.name || ''} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" id="name" name="name" />}
            </div>
            <div className="col-12 mb-3">
              <Label htmlFor="description" label={t('description')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.description || ''}
                  onChange={(e) => onFormChange('description', e.target.value)}
                  className="form-control error-description"
                  id="description"
                  name="description"
                  type="textarea"
                />
              )}
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('update')} type="submit" size="sm" width="sm" isLoading={isFormProcessing} disabled={skeleton} />
            <Button text={t('cancel')} color="light" size="sm" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
};
