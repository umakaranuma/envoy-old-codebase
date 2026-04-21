import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { FormEvent, useEffect, useState } from 'react';
import { ImageDragAndDrop } from '@/components/others/page-related/ImageDragAndDrop';
import { fileUploader } from '@/helpers/services/storageService';
import { AsyncSelect } from '@apptimus-ui/select';

import { serviceRenderPayment } from '../api-service';
import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';
import { invoicePaymentFormData } from '../../../dr-cr-note/_utils/model';
import { fetchAllUsers } from '../../../dr-cr-note/_utils/service';

interface CreatePaymentProps {
  isOpen: boolean;
  onCancel: () => void;
  afterSave: () => void;
  invoiceData: {
    id: string;
    invoiceNumber: string;
    totalAmount: number;
    outstandingAmount: number;
  };
}

export default function CreatePayment({ isOpen, onCancel, afterSave, invoiceData }: CreatePaymentProps) {
  const t = useTrans('label.invoice,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const currentUser = getLocalStorage(local_storage.auth_user_info);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    ...invoicePaymentFormData,
    invoice_amount: invoiceData.totalAmount,
    outstanding_amount: invoiceData.outstandingAmount,
    invoice_id: invoiceData.invoiceNumber,
    created_at: new Date().toISOString().split('T')[0],
    created_by: currentUser?.id,
    created_by_name: currentUser?.display_name,
  });
  const [receiptFile, setReceiptFile] = useState<File[]>([]);
  const [receiptFileError, setReceiptFileError] = useState('');

  useEffect(() => {
    setReceiptFileError('');
  }, [receiptFile]);

  const handleFormChange = (name: string, value: any) => {
    setFormData((prev) => ({ ...prev, [name]: value }));

    if (name === 'paid_amount') {
      const paidAmount = parseFloat(value) || 0;
      setFormData((prev) => ({
        ...prev,
        outstanding_amount: invoiceData.outstandingAmount - paidAmount,
      }));
    }
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    clearError(form.payments_crud.store);
    setIsSubmitting(true);

    try {
      if (receiptFile.length === 0) {
        setReceiptFileError('At least one file needs to be uploaded');
        setIsSubmitting(false);
        return;
      } else {
        setReceiptFileError('');
      }
      const receiptData = await uploadReceiptFile();

      const paymentData = {
        ...formData,
        payment_receipt_name: receiptData?.name,
        payment_receipt_url: receiptData?.doc,
        payment_receipt_type: receiptData?.type,
        service_render_id: invoiceData.id,
      };

      const response = await serviceRenderPayment(paymentData, invoiceData.id);

      if (response.status_code === 417) {
        printError(response.result, form.payments_crud.store, tBe);
        return;
      }

      if (response.is_success) {
        toaster.success(tBe(response.message));
        afterSave();
      }
    } catch (error) {
      console.error('Payment creation failed:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const uploadReceiptFile = async () => {
    if (!receiptFile) return null;

    const formData = new FormData();
    formData.append('file', receiptFile[0]);

    const fileExtension = receiptFile[0].name.split('.').pop();
    const key = await fileUploader(formData, 'envoy-test');

    return {
      doc: key,
      name: receiptFile[0].name,
      type: fileExtension,
    };
  };

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('create_new_entity', { entity: t('payments_details') })} onClose={onCancel} />

      <form onSubmit={handleSubmit} id={form.payments_crud.store}>
        <ModalBody>
          <div className="row">
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
              <Input isRequired label={t('debit_note_amount')} value={invoiceData.totalAmount} disabled name="invoice_amount" />
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
              />
            </div>

            <div className="col-12 col-md-6 mb-3">
              <Input isRequired label={t('outstanding_amount')} value={formData.outstanding_amount} className="form-control error-outstanding_amount" name="outstanding_amount" disabled />
            </div>

            <div className="col-12 col-md-6 mb-3">
              <Input label={t('remarks')} value={formData.remarks} onChange={(e) => handleFormChange('remarks', e.target.value)} className="form-control error-remarks" name="remarks" />
            </div>

            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="created_by" label={t('added_by')} isRequired />
              <AsyncSelect
                onChange={(_value: any, data: any) => {
                  setFormData((prev) => ({
                    ...prev,
                    created_by: data.id,
                    created_by_name: data.display_name,
                  }));
                  handleFormChange('created_by', data.id);
                  handleFormChange('display_name', data.display_name);
                }}
                className="form-control error-created_by"
                option={{ label: 'display_name', value: 'id' }}
                defaultValue={{
                  display_name: formData.created_by_name,
                  id: formData.created_by,
                }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllUsers(searchValue, currentPage)}
              />
            </div>

            <div className="col-12 mb-3">
              <Label htmlFor="upload_receipt" label={t('upload_receipt')} isRequired />
              <ImageDragAndDrop
                onChange={(file) => {
                  setReceiptFile(file);
                }}
                validation={{
                  maxSize: 25,
                  allowedTypes: ['pdf', 'image'],
                }}
                onError={(error) => {
                  setReceiptFileError(error);
                }}
              />
              {receiptFileError && <div className="err-msg">{receiptFileError}</div>}
            </div>
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
