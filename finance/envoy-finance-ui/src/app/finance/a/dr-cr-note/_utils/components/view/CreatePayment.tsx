import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { FormEvent, useEffect, useState } from 'react';
import { fileUploader } from '@/helpers/services/storageService';
import { AsyncSelect } from '@apptimus-ui/select';
import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';
import { invoicePaymentFormData } from '../../model';
import { createPayments } from '../../api-service';
import { fetchAllUsers } from '../../service';
import { getCurrentDate } from '@/helpers/services/commonService';
import { ImageDragAndDrop } from '@/components/others/page-related/ImageDragAndDrop';

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

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    ...invoicePaymentFormData,
    invoice_amount: invoiceData.totalAmount,
    outstanding_amount: invoiceData.outstandingAmount,
  });
  const [receiptFiles, setReceiptFiles] = useState<File[]>([]);
  const [receiptFileError, setReceiptFileError] = useState('');
  const currentUser = getLocalStorage(local_storage.auth_user_info);

  useEffect(() => {
    if (currentUser) {
      setFormData((prev) => ({
        ...prev,
        created_by: currentUser.id,
        created_by_name: currentUser.display_name,
      }));
    }
    setFormData((prev) => ({ ...prev, created_at: getCurrentDate() }));
  }, []);

  useEffect(() => {
    setReceiptFileError('');
  }, [receiptFiles]);

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
      const receiptData = await uploadReceiptFiles();
      if (!receiptData || receiptData.length === 0) {
        setReceiptFileError('At least one file needs to be uploaded');
        setIsSubmitting(false);
        return;
      } else {
        setReceiptFileError('');
      }

      const paymentData = {
        ...formData,
        payment_receipt_files: receiptData, // Array of file objects
        payment_receipt_name: receiptData[0].name, // Keep first file name for backward compatibility
        payment_receipt_url: receiptData[0].doc, // Keep first file URL for backward compatibility
        payment_receipt_type: receiptData[0].type, // Keep first file type for backward compatibility
        invoice_id: invoiceData.id,
      };

      const response = await createPayments(paymentData);

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

  const uploadReceiptFiles = async () => {
    if (!receiptFiles || receiptFiles.length === 0) return null;

    const uploadedFiles = [];

    for (const file of receiptFiles) {
      const formData = new FormData();
      formData.append('file', file);

      const fileExtension = file.name.split('.').pop();
      const key = await fileUploader(formData, 'envoy-test');

      uploadedFiles.push({
        doc: key,
        name: file.name,
        type: fileExtension,
      });
    }

    return uploadedFiles;
  };

  return (
    <Modal isOpen={isOpen} onBackdrop={onCancel} size="lg">
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
              <Input isRequired label={t('dr_cr_note_amount')} value={invoiceData.totalAmount} disabled name="invoice_amount" />
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
                  setReceiptFiles(file);
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
