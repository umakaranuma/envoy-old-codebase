import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { FormEvent, useEffect, useState } from 'react';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllInvoiceData } from '../services';
import { createPayments } from '../api-service';
import { getOneInvoice } from '../../../dr-cr-note/_utils/api-service';
import { fetchAllUsers } from '../../../dr-cr-note/_utils/service';
import FilePreviewInput from '@/components/others/page-related/uploader/FilePreviewInput';
import { handleFileUpload } from '@/helpers/services/commonService';
import { ImageDragAndDrop } from '@/components/others/page-related/uploader/ImageDragAndDrop';
import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';

interface PaymentsCreateProps {
  isOpen: boolean;
  onCancel: () => void;
  afterSave: () => void;
}

export default function PaymentsCreate({ isOpen, onCancel, afterSave }: PaymentsCreateProps) {
  const t = useTrans('label.payments,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const user = getLocalStorage(local_storage.auth_user_info);
  const [error, setError] = useState('');

  useEffect(() => {
    if (user) {
      handleFormChange('created_by', user.id);
      handleFormChange('created_by_name', user.display_name);
    }
  }, []);

  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    invoice_id: '',
    invoice_number: '',
    created_at: '',
    invoice_amount: 0,
    paid_amount: 0,
    outstanding_amount: 0,
    remarks: '',
    created_by: '',
    created_by_name: '',
    form_outstanding_amount: 0,
  });
  const [resource, setResource] = useState<File | null>(null);

  const handleFormChange = (name: string, value: any) => {
    setFormData((prev) => ({ ...prev, [name]: value }));

    if (name === 'paid_amount') {
      const paidAmount = parseFloat(value) || 0;
      setFormData((prev) => ({
        ...prev,
        form_outstanding_amount: prev.invoice_amount - paidAmount,
      }));
    }
  };

  useEffect(() => {
    console.log('formData', formData);
  }, [formData]);

  const fetchInvoiceDetails = async (invoiceId: string) => {
    try {
      const response = await getOneInvoice(invoiceId);
      if (response.is_success) {
        const invoiceData = response.result;
        const totalAmount = parseFloat(invoiceData.invoice_amount) || 0;
        const outStandAmount = parseFloat(invoiceData.outstanding_amount) || 0;

        setFormData((prev) => ({
          ...prev,
          invoice_id: invoiceData.id,
          invoice_number: invoiceData.invoice_number,
          invoice_amount: totalAmount,
          outstanding_amount: outStandAmount,
          form_outstanding_amount: outStandAmount,
        }));
      }
    } catch (error) {
      console.error('Failed to fetch invoice details:', error);
      toaster.error(tBe('error_occurred'));
    }
  };

  const handleInvoiceSelect = async (_value: any, data: any) => {
    if (data?.id) {
      await fetchInvoiceDetails(data.id);
    }
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    clearError(form.payments_crud.store);
    setError('');
    setIsSubmitting(true);

    try {
      const docData = await handleFileUpload(resource);

      const paymentData = {
        ...formData,
        payment_receipt_name: docData?.name,
        payment_receipt_url: docData?.key,
        payment_receipt_type: docData?.type,
        outstanding_amount: formData.form_outstanding_amount,
      };

      const response = await createPayments(paymentData);

      if (response.status_code === 417) {
        printError(response.result, form.payments_crud.store, tBe);
        return;
      }
      if (response.system_code === 'VALIDATION_ERROR') {
        setError(response.message);
        return;
      }

      if (response.is_success) {
        toaster.success(tBe(response.message));
        afterSave();
      }
    } catch (error) {
      console.error('Payment creation failed:', error);
      toaster.error(tBe('error_occurred'));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('add_new_payment_details')} onClose={onCancel} />
      <form onSubmit={handleSubmit} id={form.payments_crud.store}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="invoice_id" label={t('debit_note_id')} isRequired />
              <AsyncSelect
                onChange={handleInvoiceSelect}
                className="form-control error-invoice_id"
                loadOptions={(searchValue, currentPage) => fetchAllInvoiceData(searchValue, currentPage, 'PENDING')}
                option={{
                  value: 'id',
                  label: 'invoice_number',
                }}
              />
            </div>

            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="created_by" label={t('created_by')} isRequired />
              <AsyncSelect
                onChange={(_value: any, data: any) => {
                  setFormData((prev) => ({
                    ...prev,
                    created_by: data.id,
                    created_by_name: data.display_name,
                  }));
                }}
                className="form-control error-created_by"
                option={{ label: 'display_name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllUsers(searchValue, currentPage)}
                defaultValue={{ display_name: formData.created_by_name, id: formData.created_by }}
              />
            </div>

            <div className="col-12 col-md-6 mb-3">
              <Input
                isRequired
                label={t('date')}
                type="date"
                value={formData.created_at}
                onChange={(e) => handleFormChange('created_at', e.target.value)}
                className="form-control error-created_at"
                name="created_at"
              />
            </div>

            <div className="col-12 col-md-6 mb-3">
              <Input isRequired label={t('debit_note_amount')} value={formData.invoice_amount.toFixed(2)} disabled name="invoice_amount" className="form-control" />
            </div>

            <div className="col-12 col-md-6 mb-3">
              <Input
                isRequired
                label={t('paid_amount')}
                value={formData.paid_amount}
                onChange={(e) => handleFormChange('paid_amount', e.target.value)}
                className="form-control error-paid_amount"
                name="paid_amount"
                type="number"
                min="0"
                max={formData.invoice_amount}
              />
            </div>

            <div className="col-12 col-md-6 mb-3">
              <Input
                isRequired
                label={t('outstanding_amount')}
                value={formData.form_outstanding_amount.toFixed(2)}
                className="form-control error-outstanding_amount"
                name="outstanding_amount"
                disabled
              />
            </div>

            <div className="col-12 col-md-6 mb-3">
              <Input label={t('remarks')} value={formData.remarks} onChange={(e) => handleFormChange('remarks', e.target.value)} className="form-control error-remarks" name="remarks" />
            </div>

            <div className="col-12 mb-3">
              <Label htmlFor="upload_receipt" label={t('upload_receipt')} isRequired />
              {/* {!receiptFile ? (
                <ImageDragAndDrop
                  onChange={(file) => { setReceiptFile(file); }}
                  validation={{
                    maxSize: 25,
                    allowedTypes: ['pdf', 'image']
                  }}
                  onError={(error) => { setReceiptFileError(error) }}
                />
              ) : (
                <div className="d-flex flex-row justify-content-between gap-4 align-items-center border border-2 rounded-1 p-1 px-2">
                  <div>{receiptFile[0].name}</div>
                  <div className="d-flex flex-row justify-content-between gap-2">
                    <Flexicon icon="x-square" variant="line" className="text-danger action-icon" onClick={() => setReceiptFile([])} />
                  </div>
                </div>
              )} */}
              {/* {receiptFileError && (
                <div className="err-msg">
                  {receiptFileError}
                </div>
              )} */}
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
            {error && <span className="err-msg">{tBe(error)}</span>}
          </div>
        </ModalBody>

        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('cancel')} color="light" width="sm" onClick={onCancel} />
            <Button text={t('create')} type="submit" width="sm" isLoading={isSubmitting} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}
