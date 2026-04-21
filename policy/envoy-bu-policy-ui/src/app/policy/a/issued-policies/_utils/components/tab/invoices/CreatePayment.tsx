import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useEffect, useState } from 'react';
import { invoicePaymentFormData } from '../../../model';
import { createInvoicePayment, getOnePolicyInvoice } from '../../../api-service';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllUsers } from '@/app/policy/a/policy-request/_utils/services';
import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';
import { ImageDragAndDrop } from '@/components/others/page-related/uploader/ImageDragAndDrop';
import { handleFileUpload } from '@/helpers/services/commonService';
import FilePreviewInput from '@/components/others/page-related/uploader/FilePreviewInput';
import { InputSkeleton } from '@/components/others/InputSkeleton';

function CreatePayment({
  isOpen,
  onCancel,
  afterSave,
  invoiceId,
}: {
  isOpen: boolean;
  onCancel: Function;
  afterSave: Function;
  invoiceId: string;
  // paymentData: { invoiceAmount: string; outstandingAmount: string };
}) {
  const t = useTrans('label.issued_policies,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');

  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(invoicePaymentFormData);
  const [resource, setResource] = useState<File | null>(null);
  const [skeleton, setSkeleton] = useState(true);

  const user = getLocalStorage(local_storage.auth_user_info);

  useEffect(() => {
    if (user) {
      onFormChange('created_by', user.id), onFormChange('created_by_name', user.display_name);
    }
    if (invoiceId) {
      fetchData();
    }
  }, []);

  useEffect(() => {
    console.log('formData:', formData);
  }, [formData]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  // useEffect(() => {
  //   const paidAmount = parseFloat(formData.paid_amount) || 0;
  //   const outstandingAmount = parseFloat(formData.outstanding_amount) - paidAmount;
  //   onFormChange('outstanding_amount', parseFloat(outstandingAmount.toFixed(2)));
  // }, [formData.paid_amount]);
  useEffect(() => {
    const paidAmount = parseFloat(formData.paid_amount) || 0;
    // const invoiceAmount = parseFloat(formData.invoice_amount) || 0;
    console.log('paidAmount', paidAmount);

    const newOutstanding = parseFloat(formData.outstanding_amount) - paidAmount;
    onFormChange('new_outstanding_amount', parseFloat(newOutstanding.toFixed(2)));
  }, [formData.paid_amount]);

  const fetchData = async () => {
    setSkeleton(true);
    try {
      const response = await getOnePolicyInvoice(invoiceId);
      if (response.is_success) {
        onFormChange('invoice_amount', response.result.invoice_amount);
        onFormChange('outstanding_amount', response.result.outstanding_amount);
        onFormChange('new_outstanding_amount', response.result.outstanding_amount);
      }
    } catch (error) {
      console.error('An error occurred while fetching invoice data:', error);
    } finally {
      setSkeleton(false);
    }
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.payment_crud.store);
    setIsFormProcessing(true);

    try {
      const docData = await handleFileUpload(resource);
      const requestData = {
        ...formData,
        paid_amount: parseFloat(formData.paid_amount),
        outstanding_amount: formData.new_outstanding_amount,
        payment_receipt_name: docData?.name || '',
        payment_receipt_url: docData?.key || '',
        invoice_id: invoiceId,
      };
      const responseData = await createInvoicePayment(requestData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.payment_crud.store, tBe);
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
      <ModalHeader title={t('create_new_entity', { entity: t('payments_details') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.payment_crud.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Input
                isRequired
                label={t('date')}
                value={formData.created_at}
                onChange={(e) => onFormChange('created_at', e.target.value)}
                className="form-control error-created_at"
                name="created_at"
                type="date"
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('debit_note_amount')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.invoice_amount}
                  disabled
                  // onChange={(e) => onFormChange('invoice_amount', e.target.value)}
                  // className="form-control error-invoice_amount"
                  name="invoice_amount"
                />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                isRequired
                label={t('paid_amount')}
                value={formData.paid_amount}
                onChange={(e) => onFormChange('paid_amount', e.target.value)}
                className="form-control error-paid_amount"
                name="paid_amount"
                type="number"
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('outstanding_amount')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={parseFloat(formData.new_outstanding_amount).toFixed(2).toString() || 0}
                  // onChange={(e) => onFormChange('outstanding_amount', e.target.value)}
                  // className="form-control error-outstanding_amount"
                  // name="outstanding_amount"
                  disabled
                />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="created_by" label={t('created_by')} isRequired />
              <AsyncSelect
                onChange={(_value: any, data: any) => {
                  setFormData({ ...formData, created_by: data.id, created_by_name: data.display_name });
                  onFormChange('created_by', data.id), onFormChange('display_name', data.display_name);
                }}
                className="form-control error-created_by"
                option={{ label: 'display_name', value: 'id' }}
                defaultValue={{ display_name: formData.created_by_name, id: formData.created_by }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllUsers(searchValue, currentPage)}
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                isRequired
                label={t('reference_id')}
                value={formData.reference_id}
                onChange={(e) => onFormChange('reference_id', e.target.value)}
                className="form-control error-reference_id"
                name="reference_id"
                type="text"
              />
            </div>
            <div className="col-12 mb-3">
              <Label htmlFor="upload_receipt" label={t('upload_receipt')} isRequired />
              {!resource ? (
                <ImageDragAndDrop htmlFor={'document'} selectedImage={(file: File) => setResource(file)} className="form-control error-payment_receipt_url" />
              ) : (
                <FilePreviewInput
                  fileName={resource?.name || ''}
                  onCancel={() => {
                    setResource(null);
                  }}
                />
              )}
            </div>
            <div className="col-12">
              <Input
                type="textarea"
                rows={3}
                label={t('remarks')}
                value={formData.remarks}
                onChange={(e) => onFormChange('remarks', e.target.value)}
                className="form-control error-remarks"
                name="remarks"
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

export default CreatePayment;
