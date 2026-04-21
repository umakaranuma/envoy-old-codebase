import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { FormEvent, useEffect, useState } from 'react';
import { AsyncSelect } from '@apptimus-ui/select';
import { addSettlement, getOneAgentCommissionSettlements } from '../api-service';
import { fetchAllUsers } from '../../../dr-cr-note/_utils/service';
import { InputSkeleton } from '@/components/others/InputSkeleton';

export default function AddSettlement({ isOpen, onCancel, afterSave, currentSettlementId }: { isOpen: boolean; onCancel: () => void; afterSave: Function; currentSettlementId: string }) {
  const t = useTrans('label.payments,label.commission,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [error, setError] = useState('');
  const [skeleton, setSkeleton] = useState(false);

  useEffect(() => {
    if (currentSettlementId) {
      fetchInvoiceDetails();
    }
  }, [currentSettlementId]);

  const [isSubmitting, setIsSubmitting] = useState(false);

  const [formData, setFormData] = useState({
    pay_amount: '',
    agent_name: '',
    created_at: '',
    agent_id: 0,
    outstanding_amount: 0,
    form_outstanding_amount: 0,
  });

  const handleFormChange = (name: string, value: any) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const fetchInvoiceDetails = async () => {
    try {
      setSkeleton(true);
      const response = await getOneAgentCommissionSettlements(currentSettlementId);
      if (response.is_success) {
        const invoiceData = response.result;
        const outStandAmount = parseFloat(invoiceData.outstanding) || 0;

        setFormData((prev) => ({
          ...prev,
          agent_name: invoiceData.agent_name,
          agent_id: invoiceData.agent_id,
          outstanding_amount: outStandAmount,
          form_outstanding_amount: outStandAmount,
        }));
        setSkeleton(false);
      }
    } catch (error) {
      toaster.error(tBe('error_occurred'));
    }
  };

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    clearError(form.payments_crud.store);
    setError('');
    setIsSubmitting(true);

    try {
      const response = await addSettlement(formData, currentSettlementId);

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
      <ModalHeader title={t('add_settlement')} onClose={onCancel} />
      <form onSubmit={handleSubmit} id={form.payments_crud.store}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="created_by" label={t('created_by')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <AsyncSelect
                  onChange={(_value: any, data: any) => {
                    setFormData((prev) => ({
                      ...prev,
                      agent_id: data.id,
                      agent_name: data.display_name,
                    }));
                  }}
                  className="form-control error-agent_name"
                  option={{ label: 'display_name', value: 'id' }}
                  isSearchable={true}
                  loadOptions={(searchValue, currentPage) => fetchAllUsers(searchValue, currentPage)}
                  defaultValue={{ display_name: formData.agent_name, id: formData.agent_id }}
                />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                isRequired
                label={t('date')}
                type="date"
                value={new Date().toISOString().split('T')[0]}
                onChange={(e) => handleFormChange('created_at', e.target.value)}
                className="form-control error-created_at"
                name="created_at"
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                isRequired
                label={t('paid_amount')}
                value={formData.pay_amount}
                onChange={(e) => handleFormChange('pay_amount', e.target.value)}
                className="form-control error-pay_amount"
                name="paid_amount"
                type="number"
                min="0"
                max={formData.pay_amount}
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
