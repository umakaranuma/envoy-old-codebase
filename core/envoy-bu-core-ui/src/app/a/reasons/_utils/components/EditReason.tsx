import { useTrans } from '@/helpers/services/lang/langService';
import React, { FormEvent, useEffect, useState } from 'react';
import { initFormData, IReasonData } from '../model';
import { getOneReason, updateReason } from '../api-service';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label, Skeleton } from '@apptimus-ui/ui-element';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllEndorsementTypes } from '../services';

export const EditReason = ({ isOpen, editId, afterUpdate, onCancel }: { isOpen: boolean; editId: string; onCancel: Function; afterUpdate: Function }) => {
  const t = useTrans('label.reason,otr.common');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);
  const [skeleton, setSkeleton] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneReason(editId);

      if (responseData?.is_success) {
        const data: IReasonData = responseData.result;
        onFormChange('type', data.type);
        onFormChange('type_id', data.type_id);
        onFormChange('reason', data.reason);
        onFormChange('allows_custom_reason', data.allows_custom_reason);
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
    clearError(form.reasons_crud.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updateReason(editId, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.reasons_crud.update, tBe);
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
      <ModalHeader title={t('edit_entity', { entity: t('reason') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.reasons_crud.update}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3 custom-select">
              <Label htmlFor="type" label={t('reason_type')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <AsyncSelect
                  onChange={(_, data) => {
                    onFormChange('type_id', data.id);
                    onFormChange('type', data.name);
                  }}
                  className="form-control error-type_id"
                  option={{ label: 'name', value: 'id' }}
                  isSearchable={true}
                  loadOptions={(searchValue, currentPage) => fetchAllEndorsementTypes(searchValue, currentPage)}
                  defaultValue={{ name: formData.type, id: formData.type_id }}
                />
              )}
            </div>
            <div className="col-12 mb-3">
              <Label htmlFor="reason" label={t('reason')} isRequired />
              {skeleton ? (
                <Skeleton height="62.78px" />
              ) : (
                <Input value={formData.reason || ''} onChange={(e) => onFormChange('reason', e.target.value)} className="form-control error-reason" id="reason" name="reason" type="textarea" />
              )}
            </div>
            <div className="mb-3">
              {skeleton ? (
                <Skeleton height="20px" />
              ) : (
                <>
                  <input type="checkbox" checked={formData.allows_custom_reason} onChange={(e) => onFormChange('allows_custom_reason', e.target.checked)} />
                  <span className="ms-2 fs-14">{t('allow_custom_reason')}</span>
                </>
              )}
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
            <Button text={t('update')} type="submit" width="sm" isLoading={isFormProcessing} disabled={skeleton} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
};
