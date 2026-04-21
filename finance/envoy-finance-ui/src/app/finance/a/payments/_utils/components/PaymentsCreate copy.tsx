import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { initFormData } from '../model';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { createPayments } from '../api-service';
import { AsyncSelect, Select } from '@apptimus-ui/select';
import { fetchAllInvoiceData } from '../services';

function PaymentsCreate({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);
  const [formMode, setFormMode] = useState<'create' | 'reverse'>('create'); // Track form mode
  const [showOutwardFields, setShowOutwardFields] = useState(false);

  const t = useTrans('label.payments,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');

  const resetForm = () => {
    setFormData(initFormData);
    setFormMode('create');
    setShowOutwardFields(false);
  };

  const onFormChange = (name: string, value: any) => {
    // Handle payment type change
    if (name === 'invoice_payment_type') {
      const isOutward = value === 'Outward';
      setShowOutwardFields(isOutward);

      // Reset outward payment type when changing payment type
      if (!isOutward) {
        setFormData((prev) => ({ ...prev, outward_payment_type: '' }));
      }
    }

    // Handle outward payment type change
    if (name === 'outward_payment_type') {
      if (value === 'Reverse Payment') {
        setFormMode('reverse');
      } else {
        setFormMode('create');
      }
    }

    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  const handleCancel = () => {
    resetForm();
    onCancel();
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.payments_crud.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createPayments(formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.payments_crud.store, tBe);
      }

      if (responseData.is_success) {
        afterSave();
        toaster.success(tBe(responseData.message));
        resetForm();
      }
    } catch (error) {
      console.error('An error occurred:', error);
      setIsFormProcessing(false);
    }
  }

  // Determine modal title based on form mode
  const getModalTitle = () => {
    return formMode === 'reverse' ? t('reverse_payment_with_credit_note') : t('add_new_payment_details');
  };

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={getModalTitle()} onClose={handleCancel} />
      <form onSubmit={onSubmit} id={`${form.payments_crud.store}`}>
        <ModalBody>
          {/* Always show these basic fields */}
          <div className="row">
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="invoice_no" label={t('invoice_no')} isRequired />
              <AsyncSelect
                defaultValue={formData.invoice_no}
                onChange={(value) => onFormChange('invoice_no', value)}
                className="form-control error-invoice_no"
                loadOptions={fetchAllInvoiceData}
                option={{
                  value: 'id',
                  label: 'invoice_name',
                }}
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                isRequired
                label={t('payment_date')}
                value={formData.payment_date}
                onChange={(e) => onFormChange('payment_date', e.target.value)}
                className="form-control error-payment_date"
                name="payment_date"
                type="date"
              />
            </div>
          </div>

          {/* Show different fields based on form mode */}
          {formMode === 'create' ? (
            <>
              {/* Create Payment Mode */}
              <div className="row">
                <div className="col-12 col-md-6 mb-3">
                  <Input
                    isRequired
                    label={t('policy_info')}
                    value={formData.policy_info}
                    onChange={(e) => onFormChange('policy_info', e.target.value)}
                    className="form-control error-policy_info"
                    name="policy_info"
                  />
                </div>
                <div className="col-12 col-md-6 mb-3 custom-select">
                  <Label label={t('payment_type')} isRequired />
                  <Select
                    onChange={(value) => onFormChange('invoice_payment_type', value)}
                    className="form-control error-invoice_payment_type"
                    option={{
                      value: 'value',
                      label: 'label',
                      keysToSearch: ['label'],
                    }}
                    options={[
                      { label: t('inward'), value: 'Inward' },
                      { label: t('outward'), value: 'Outward' },
                    ]}
                    defaultValue={formData.invoice_payment_type}
                  />
                </div>
              </div>

              {/* Outward Payment Type Fields (shown when invoice_payment_type is Outward) */}
              {showOutwardFields && (
                <div className="row">
                  <div className="col-12 mb-3">
                    <div className="form-group">
                      <Label label={t('outward_payment_type')} isRequired />
                      <div className="d-flex gap-4">
                        <div className="d-flex col-12 col-md-6 align-items-center gap-2">
                          <Input
                            type="radio"
                            id="reverse-payment"
                            name="outward_payment_type"
                            value="Reverse Payment"
                            checked={formData.outward_payment_type === 'Reverse Payment'}
                            onChange={() => onFormChange('outward_payment_type', 'Reverse Payment')}
                            className="mb-2"
                          />
                          <Label label={t('reverse_payment')} />
                        </div>
                        <div className="d-flex col-12 col-md-6 align-items-center gap-2">
                          <Input
                            type="radio"
                            id="normal-payment"
                            name="outward_payment_type"
                            value="Normal Payment"
                            checked={formData.outward_payment_type === 'Normal Payment'}
                            onChange={() => onFormChange('outward_payment_type', 'Normal Payment')}
                            className="mb-2"
                          />
                          <Label htmlFor="normal-payment" label={t('normal_payment')} />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div className="row">
                <div className="col-12 col-md-6 mb-3">
                  <Input
                    isRequired
                    label={t('amount_paid')}
                    value={formData.amount_paid}
                    onChange={(e) => onFormChange('amount_paid', e.target.value)}
                    className="form-control error-amount_paid"
                    name="amount_paid"
                    type="number"
                  />
                </div>
                <div className="col-12 col-md-6 mb-3">
                  <Input label={t('remarks')} value={formData.remarks} onChange={(e) => onFormChange('remarks', e.target.value)} className="form-control error-remarks" name="remarks" />
                </div>
              </div>
            </>
          ) : (
            <>
              {/* Reverse Payment Mode */}
              <div className="row">
                <div className="col-12 col-md-6 mb-3">
                  <Input
                    isRequired
                    label={t('payment_id')}
                    value={formData.payment_id}
                    onChange={(e) => onFormChange('payment_id', e.target.value)}
                    className="form-control error-payment_id"
                    name="payment_id"
                  />
                </div>
                <div className="col-12 col-md-6 mb-3">
                  <Input
                    isRequired
                    label={t('original_payment_amount')}
                    value={formData.original_payment_amount}
                    onChange={(e) => onFormChange('original_payment_amount', e.target.value)}
                    className="form-control error-original_payment_amount"
                    name="original_payment_amount"
                  />
                </div>
              </div>

              <div className="row">
                <h6 className="mb-2" style={{ fontSize: '14px' }}>
                  {t('reason_for_reversal')}
                </h6>
                <div className="col-12 mb-3">
                  <Input
                    isRequired
                    label={t('reason_for_reversal')}
                    value={formData.reason_for_reversal}
                    onChange={(e) => onFormChange('reason_for_reversal', e.target.value)}
                    className="form-control error-reason_for_reversal"
                    name="reason_for_reversal"
                  />
                </div>
              </div>

              <div className="row">
                <div className="col-12 col-md-6 mb-3">
                  <Input
                    isRequired
                    label={t('credit_note_id')}
                    value={formData.credit_note_id}
                    onChange={(e) => onFormChange('credit_note_id', e.target.value)}
                    className="form-control error-credit_note_id"
                    name="credit_note_id"
                  />
                </div>
                <div className="col-12 col-md-6 mb-3">
                  <Input
                    isRequired
                    label={t('effective_date')}
                    value={formData.effective_date}
                    onChange={(e) => onFormChange('effective_date', e.target.value)}
                    className="form-control error-effective_date"
                    name="effective_date"
                    type="date"
                  />
                </div>
              </div>

              <div className="row">
                <div className="col-12 mb-3">
                  <div className="row">
                    <div className="col-12 col-md-6 mb-3">
                      <Input
                        isRequired
                        type="number"
                        label={t('credit_note_amount')}
                        value={formData.credit_note_amount}
                        onChange={(e) => onFormChange('credit_note_amount', e.target.value)}
                        className="form-control error-credit_note_amount"
                        name="credit_note_amount"
                      />
                    </div>
                    <div className="col-12 col-md-6 mb-3">
                      <Input
                        label={t('date')}
                        value={formData.credit_note_date}
                        onChange={(e) => onFormChange('credit_note_date', e.target.value)}
                        className="form-control error-credit_note_date"
                        name="credit_note_date"
                        type="date"
                      />
                    </div>
                    <div className="col-12 mb-3">
                      <Input
                        label={t('remarks')}
                        value={formData.credit_note_remarks}
                        onChange={(e) => onFormChange('credit_note_remarks', e.target.value)}
                        className="form-control error-credit_note_remarks"
                        name="credit_note_remarks"
                        type="textarea"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('cancel')} color="light" width="sm" onClick={handleCancel} />
            <Button text={t('create')} type="submit" width="sm" isLoading={isFormProcessing} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default PaymentsCreate;
