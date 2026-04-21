import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useEffect, useState } from 'react';
import { initFormData } from '../model';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { createServiceRendered } from '../api-service';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllPaymentStatus, fetchAllServiceRenderTypes } from '../services';
import { getOneServiceRenderedFee } from '../api-service';
import { fetchAllCustomers, fetchAllUsers } from '../../../dr-cr-note/_utils/service';
import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';

function ServiceRenderedCreate({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);
  const t = useTrans('label.service_rendered,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const user = getLocalStorage(local_storage.auth_user_info);

  useEffect(() => {
    if (user) {
      onFormChange('service_provider_id', user.id);
      onFormChange('service_provider_name', user.display_name);
    }
  }, []);

  useEffect(() => {
    onFormChange('service_date', new Date().toISOString().split('T')[0]);
  }, [isOpen]);

  const onFormChange = async (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));

    if (name === 'service_id' && value) {
      try {
        const response = await getOneServiceRenderedFee(value);

        if (response.is_success) {
          setFormData((prevFormData) => ({
            ...prevFormData,
            standard_fee: response.result[0].fee || 0,
          }));
        }
      } catch (error) {
        console.error('Error fetching service fee:', error);
      }
    }
  };

  const formatDateToMMDDYYYY = (dateStr: string) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    const year = date.getFullYear();
    return `${month}/${day}/${year}`;
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.service_rendered.store);
    setIsFormProcessing(true);

    try {
      const payload = {
        user_id: formData.service_provider_id || '',
        service_id: formData.service_id || '',
        service_date: formatDateToMMDDYYYY(formData.service_date),
        fee: Number(formData.standard_fee || 0),
        invoice_status: formData.invoice_status || 1,
        payment_status: formData.payment_status || '',
        remarks: formData.remarks || '',
        customer_id: formData.customer_id || '',
      };

      const responseData = await createServiceRendered(payload);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.service_rendered.store, tBe);
      }

      if (responseData.is_success) {
        afterSave();
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
      setIsFormProcessing(false);
    }
  }

  return (
    <Modal isOpen={isOpen} onBackdrop={() => onCancel()}>
      <ModalHeader title={t('add_new_service_rendered')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.service_rendered.store}`}>
        <ModalBody>
          <div className="row">
            {/* <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="invoice_no" label={t('invoice_no')} isRequired />
              <AsyncSelect
                defaultValue={formData.invoice_no}
                onChange={(value) => onFormChange('invoice_no', value)}
                className="form-control error-invoice_no"
                loadOptions={fetchAllInvoice}
                option={{
                  value: 'id',
                  label: 'invoice_number',
                }}
              />
            </div> */}
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="customer_id" label={t('customer')} isRequired />
              <AsyncSelect
                onChange={(_value: any, data: any) => {
                  setFormData((prev) => ({
                    ...prev,
                    customer_id: data.id,
                    created_by_name: data.name,
                  }));
                }}
                className="form-control error-customer_id"
                option={{ label: 'name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllCustomers(searchValue, currentPage)}
              />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="service_provider_id" label={t('service_provider_name')} />
              <AsyncSelect
                onChange={(_value: any, data: any) => {
                  setFormData((prev) => ({
                    ...prev,
                    service_provider_id: data.id,
                  }));
                }}
                className="form-control error-service_provider_id"
                option={{ label: 'display_name', value: 'id' }}
                isSearchable={true}
                defaultValue={{ display_name: formData.service_provider_name, id: formData.service_provider_id }}
                loadOptions={(searchValue, currentPage) => fetchAllUsers(searchValue, currentPage)}
              />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="service_id" label={t('service_rendered')} isRequired />
              <AsyncSelect
                defaultValue={formData.service_id}
                onChange={(value) => onFormChange('service_id', value)}
                className="form-control error-service_id"
                loadOptions={fetchAllServiceRenderTypes}
                option={{
                  value: 'id',
                  label: 'title',
                }}
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                isRequired
                label={t('service_date')}
                value={formData.service_date || ''}
                onChange={(e) => onFormChange('service_date', e.target.value)}
                className="form-control error-service_date"
                name="service_date"
                type="date"
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                isRequired
                label={t('standard_fee')}
                value={formData.standard_fee || 0}
                onChange={(e) => onFormChange('standard_fee', e.target.value)}
                className="form-control error-standard_fee"
                name="standard_fee"
                type="number"
                // disabled
              />
            </div>
            {/* <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="invoice_status" label={t('invoice_status')} isRequired />
              <AsyncSelect
                defaultValue={formData.invoice_status}
                onChange={(value) => onFormChange('invoice_status', value)}
                className="form-control error-invoice_status"
                loadOptions={fetchAllInvoiceStatus}
                option={{
                  value: 'id',
                  label: 'name',
                }}
              />
            </div> */}
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="payment_status" label={t('payment_status')} isRequired />
              <AsyncSelect
                defaultValue={formData.payment_status}
                onChange={(value) => onFormChange('payment_status', value)}
                className="form-control error-payment_status"
                loadOptions={fetchAllPaymentStatus}
                option={{
                  value: 'id',
                  label: 'name',
                }}
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input label={t('remarks')} value={formData.remarks || ''} onChange={(e) => onFormChange('remarks', e.target.value)} className="form-control error-remarks" name="remarks" />
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
            <Button text={t('create')} type="submit" width="sm" isLoading={isFormProcessing} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default ServiceRenderedCreate;
