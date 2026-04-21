'use client';
import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { initCustomerFormData } from '../../model';
import { toaster } from '@/helpers/services/toaster';
import { createCustomers } from '../../api-service';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { Select } from '@apptimus-ui/select';

function CustomersCreate({ isOpen, onCancel }: { isOpen: boolean; onCancel: Function }) {
  const t = useTrans('label.customers,otr.common');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initCustomerFormData);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  const tBe = useTrans('be.msg,be.error,be.attri');
  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.customres_crud.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createCustomers(formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.customres_crud.store, tBe);
      }

      if (responseData.is_success) {
        onCancel();
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen} size="lg">
      <ModalHeader title={t('add_new_entity', { entity: t('customer') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.customres_crud.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('customer_type')} isRequired />
              <Select
                onChange={(value) => onFormChange('type', value)}
                className="form-control"
                options={[
                  { label: t('corporate'), value: 'Corporate' },
                  { label: t('personal'), value: 'Personal' },
                ]}
                option={{ label: 'label', value: 'value' }}
                isSearchable={false}
              />
              <span className="error-type"></span>
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input isRequired label={t('customer_name')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
          </div>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Input label={t('remarks')} value={formData.remarks} onChange={(e) => onFormChange('remarks', e.target.value)} className="form-control error-remarks" name="remarks" />
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

export default CustomersCreate;
