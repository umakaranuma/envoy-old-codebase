import { Description } from '@/components/others/Description';
import { ImageDragAndDrop } from '@/components/others/page-related/ImageDragAndDrop';
import UploadedFile from '@/components/others/page-related/UploadedFile';
import { form } from '@/constans/Form';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { AsyncSelect } from '@apptimus-ui/select';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { IPaymentDetails, IPaymentFormData } from '../../../model';
import { fetchAllInvoices } from '../../../service';
import { addSettlement, getOnePolicyBankInfo } from '../../../api-service';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { toaster } from '@/helpers/services/toaster';
import { fileUploader } from '@/helpers/services/storageService';
import { useParams } from 'next/navigation';

function MakePayment({ isOpen, onCancel, afterSubmit, selectedPolicyId }: { isOpen: boolean; onCancel: Function; afterSubmit: Function; selectedPolicyId: string }) {
  const t = useTrans('label.my_policy,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [skeleton, setSkeleton] = useState(true);
  const [data, setData] = useState({} as IPaymentDetails);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState<IPaymentFormData>({
    paid_amount: '',
    endorsement_type_id: '',
    invoice_amount: '0',
    outstanding_amount: '0',
    payment_method: '',
    file: null,
    reference_id: '',
    invoice_number: '',
    previous_outstanding_amount: '0',
  });
  const params = useParams();
  const appId = params.appId as string;

  useEffect(() => {
    const fetchData = async () => {
      setSkeleton(true);
      const responseData = await getOnePolicyBankInfo(selectedPolicyId);
      if (responseData?.is_success) {
        if (responseData.result.bank_details === null || responseData.result === null) {
          setError('bank_details_not_found');
          return;
        }
        setData(responseData.result);
        if (!responseData.result?.payment_gateway_url) {
          onFormChange('payment_method', 'bank_transfer');
        }
      }
      setSkeleton(false);
    };
    fetchData();
  }, []);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    // handleOpenReceipt();
    if (formData.payment_method === 'online') {
      onRedirectToPaymentGateway();
      return;
    }
    clearError(form.settlement.store);
    setIsFormProcessing(true);
    try {
      const receipt = await handleFileUpload(formData.file ?? null);
      const responseData = await addSettlement({ ...formData, policy_id: selectedPolicyId, receipt: receipt?.doc ?? null, receipt_name: receipt?.name ?? null, receipt_type: receipt?.type ?? null });
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.settlement.store, tBe);
      }

      if (responseData.is_success) {
        setFormData({
          paid_amount: '',
          endorsement_type_id: '',
          invoice_amount: 'LKR 0.00',
          outstanding_amount: 'LKR 0.00',
          payment_method: '',
          file: null,
          reference_id: '',
          invoice_number: '',
        });
        toaster.success(tBe(responseData.message));
        handleOpenReceipt();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  const handleOpenReceipt = () => {
    onCancel();
    setTimeout(() => {
      afterSubmit(formData.payment_method, formData.invoice_number);
    }, 100);
  };

  const handleFileUpload = async (file: File | null) => {
    const fileData = new FormData();
    if (!file) {
      return null;
    }
    fileData.append('file', file);
    const fileName = file.name;
    const fileExtension = file.name.split('.').pop();
    const key = await fileUploader(fileData, `${appId}/customer/policy-settlement`);
    return { doc: key, name: fileName, type: fileExtension };
  };

  const onRedirectToPaymentGateway = () => {
    if (data.payment_gateway_url) {
      window.open(data.payment_gateway_url, '_blank');
    } else {
      toaster.error(tBe('payment_method_not_available'));
    }
  };

  useEffect(() => {
    console.log('outstanding_amount:', formData.outstanding_amount);
  }, [formData.outstanding_amount]);

  return (
    <Modal isOpen={isOpen} size="lg" scrollable>
      <ModalHeader title={t('make_a_payment')} onClose={() => onCancel()} />
      <ModalBody>
        <div id={`${form.settlement.store}`}>
          <div className="row">
            <div className="fs-13 fw-semibold mb-3">{t('payment_information')}</div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('select_invoice')} isRequired />
              <AsyncSelect
                onChange={(_value, data) => {
                  onFormChange('invoice_id', data.id);
                  onFormChange('invoice_amount', data.total_amount);
                  onFormChange('invoice_number', data.invoice_number);
                  onFormChange('outstanding_amount', data.outstanding_amount);
                  onFormChange('previous_outstanding_amount', data.outstanding_amount);
                }}
                className="form-control error-invoice_id"
                option={{ label: 'invoice_number', value: 'id' }}
                isSearchable={false}
                loadOptions={(searchValue: any, currentPage: any) => fetchAllInvoices(searchValue, currentPage, selectedPolicyId)}
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input label={t('debit_note_number')} value={parseFloat(formData.invoice_amount).toFixed(2)} className="form-control error-cover_value" name="cover_values" disabled />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                label={t('paid_amount')}
                isRequired
                value={formData.paid_amount}
                className="form-control error-paid_amount"
                name="paid_amount"
                onChange={(e) => {
                  onFormChange('paid_amount', e.target.value);
                  onFormChange('outstanding_amount', parseFloat(formData.previous_outstanding_amount || '0') - parseFloat(e.target.value || '0'));
                }}
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                label={t('outstanding_amount')}
                value={formData.outstanding_amount ? parseFloat(formData.outstanding_amount).toFixed(2) : ''}
                className="form-control error-outstanding_amount"
                name="outstanding_amount"
                disabled
              />
            </div>
          </div>
          <div>
            <div className="fs-13 fw-semibold mb-3">{t('payment_method')}</div>
            <div className="mb-3 d-flex flex-row gap-2 align-items-center">
              {data.payment_gateway_url && (
                <>
                  <input type="radio" id="online" name="payment_method" value="online" className="mb-2" onChange={(e) => onFormChange('payment_method', e.target.value)} />
                  <Label htmlFor="online" label={t('online')} />
                </>
              )}
              <input
                type="radio"
                id="bank_transfer"
                checked={formData.payment_method === 'bank_transfer'}
                name="payment_method"
                value="bank_transfer"
                className="mb-2"
                onChange={(e) => onFormChange('payment_method', e.target.value)}
              />
              <Label htmlFor="bank_transfer" label={t('bank_transfer')} />
            </div>
          </div>
          {formData.payment_method === 'bank_transfer' && (
            <>
              {error === 'bank_details_not_found' ? (
                <div className="text-danger fs-13 text-center">{t('bank_details_not_found')}</div>
              ) : (
                <div className="row">
                  <div className="fs-13 fw-semibold mb-3">{t('bank_account_info')}</div>
                  <div className="col-12 col-md-6 mb-3">
                    <Description label={t('account_holder_name')} value={data.bank_details.account_holder_name} skeleton={skeleton} />
                  </div>
                  <div className="col-12 col-md-6 mb-3">
                    <Description label={t('account_number')} value={data.bank_details.account_number} skeleton={skeleton} />
                  </div>
                  <div className="col-12 col-md-6 mb-3">
                    <Description label={t('bank_name')} value={data.bank_details.bank_name} skeleton={skeleton} />
                  </div>
                  <div className="col-12 col-md-6 mb-3">
                    <Description label={t('bank_branch')} value={data.bank_details.bank_branch} skeleton={skeleton} />
                  </div>
                  <div className="col-12 mb-3">
                    <Description label={t('iban_swift_code_for_international_if_needed')} value={data.bank_details.iban_swift_code} skeleton={skeleton} />
                  </div>
                  <div className="col-12 col-md-6 mb-3">
                    <Input
                      label={t('reference_id')}
                      isRequired
                      value={formData.reference_id}
                      className="form-control error-reference_id"
                      name="reference_id"
                      onChange={(e) => {
                        onFormChange('reference_id', e.target.value);
                      }}
                    />
                  </div>
                  <div className="col-12 mb-3">
                    <Label label={t('upload_receipt')} isRequired />
                    {formData.file ? (
                      <UploadedFile fileName={formData.file.name} fileSize={`${(formData.file.size / 1024).toFixed(2)} MB`} onRemove={() => onFormChange('file', null)} />
                    ) : (
                      <ImageDragAndDrop htmlFor={'receipt'} selectedImage={(file: File) => onFormChange('file', file)} className="form-control error-receipt" />
                    )}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          <Button text={t(`${formData.payment_method === 'bank_transfer' ? 'submit' : 'continue'}`)} type="submit" width="sm" isLoading={isFormProcessing} onClick={onSubmit} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default MakePayment;
