import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { AsyncSelect, Select } from '@apptimus-ui/select';
import { fetchAllFormsData } from '../../../../services';
import { createFormConfig } from '../../../../api-service';

function ConfigureForm({ isOpen, onCancel, afterSave, viewId }: { isOpen: boolean; onCancel: Function; afterSave: Function; viewId: string }) {
  const t = useTrans('label.form,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    form_id: '',
    data_gethering_type: '',
    opportunity_type_id: viewId,
  });

  const data = [
    {
      id: 1,
      label: t('onboarding'),
      type: 'ONBOARDING',
    },
    {
      id: 2,
      label: t('claim'),
      type: 'CLAIM',
    },
    {
      id: 3,
      label: t('claim_evaluation'),
      type: 'CLAIM_EVALUATION',
    },
    {
      id: 4,
      label: t('customer_policy'),
      type: 'CUSTOMER_POLICY',
    },
  ];

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.form_crud.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createFormConfig(viewId, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.form_crud.store, tBe);
      }

      if (responseData.is_success) {
        afterSave();
        setFormData({
          title: '',
          form_id: '',
          data_gethering_type: '',
          opportunity_type_id: viewId,
        });
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('add_new_entity', { entity: t('form') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.form_crud.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Input isRequired label={t('title')} value={formData.title} onChange={(e) => onFormChange('title', e.target.value)} className="form-control error-title" name="title" />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="form" label={t('form')} isRequired />
              <AsyncSelect
                onChange={(value) => onFormChange('form_id', value)}
                className="form-control error-form_id"
                loadOptions={fetchAllFormsData}
                option={{
                  value: 'id',
                  label: 'title',
                }}
              />
            </div>

            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="form" label={t('type')} isRequired />
              <Select
                onChange={(_, data) => {
                  onFormChange('data_gethering_type', data.type);
                }}
                options={data}
                option={{
                  label: 'label',
                  value: 'id',
                  keysToSearch: ['label', 'id'],
                }}
              />
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

export default ConfigureForm;
