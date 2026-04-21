import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { initFlagData, IResons } from '../../model';
import { toaster } from '@/helpers/services/toaster';
import { createFlag } from '../../api-service';
import { useTrans } from '@/helpers/services/lang/langService';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllFlagType, fetchAllReasons } from '../../services';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';

function FlagCreate({ isOpen, onCancel, afterSave, entityId }: { isOpen: boolean; onCancel: Function; afterSave: Function; entityId: string }) {
  if (!isOpen) {
    return null;
  }

  const t = useTrans('label.sales_managements,otr.common,be.msg');

  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFlagData);
  const [reasonsData, setReasonsData] = useState({} as IResons);
  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };
  const tBe = useTrans('be.msg,be.error,be.attri');

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.flag_crud.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createFlag(entityId, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.flag_crud.store, tBe);
      }

      if (responseData.system_code === 'FLAG_ALREADY_ADDED') {
        toaster.error(tBe(responseData.message));
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
      <ModalHeader title={t('create_new_entity', { entity: t('flag') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.flag_crud.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-12 mb-3 custom-select">
              <Label htmlFor="flag_type" label={t('flag_type')} isRequired />
              <AsyncSelect
                onChange={(value) => onFormChange('flag_id', value)}
                className="form-control error-flag_id"
                option={{ label: 'name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllFlagType(searchValue, currentPage, entityId)}
              />
            </div>
            <div className="col-12 col-md-12 mb-3 custom-select">
              <Label htmlFor="reason" label={t('reason')} />
              <AsyncSelect
                onChange={(value, data) => {
                  onFormChange('reason_id', value), setReasonsData(data);
                }}
                className="form-control error-reason_id"
                option={{ label: 'reason', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllReasons(searchValue, currentPage)}
              />
            </div>
            {reasonsData?.allows_custom_reason === 1 && (
              <div className="col-12 col-md-12 mb-3">
                <Input
                  label={t('customer_reason')}
                  value={formData.customer_reason}
                  onChange={(e) => onFormChange('customer_reason', e.target.value)}
                  className="form-control error-customer_reason"
                  name="customer_reason"
                  type="textarea"
                />
              </div>
            )}
            <div className="col-12 col-md-12 mb-3">
              <Input label={t('remarks')} value={formData.remarks} onChange={(e) => onFormChange('remarks', e.target.value)} className="form-control error-remarks" name="remarks" />
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('save')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default FlagCreate;
