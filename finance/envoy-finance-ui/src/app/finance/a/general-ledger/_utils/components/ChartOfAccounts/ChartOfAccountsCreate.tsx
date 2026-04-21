import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { Select } from '@apptimus-ui/select';
import { initFormData } from '../../model';
import { createchartOfAccounts } from '../../api-service';

function ChartOfAccountsCreate({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);
  const t = useTrans('label.general_ledger,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.chart_of_accounts_crud.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createchartOfAccounts(formData);
      setIsFormProcessing(false);
      if (responseData.status_code === 417) {
        printError(responseData.result, form.chart_of_accounts_crud.store, tBe);
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
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('add_new_chart_of_accounts_details')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.chart_of_accounts_crud.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('account_name')} isRequired />
              <Input
                value={formData.account_name}
                onChange={(e) => onFormChange('account_name', e.target.value)}
                className="form-control error-account_name"
                name="account_name"
                placeholder={t('enter_account_name')}
              />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('account_type')} isRequired />
              <Select
                onChange={(_e, data) => onFormChange('account_type', data?.value || '')}
                options={[
                  { label: 'Asset', value: 'asset' },
                  { label: 'Liability', value: 'liability' },
                  { label: 'Equity', value: 'equity' },
                  { label: 'Revenue', value: 'revenue' },
                  { label: 'Expense', value: 'expense' },
                ]}
                option={{ label: 'label', value: 'value' }}
                isSearchable={false}
                className="form-control error-account_type"
                placeholder={t('select_account_type')}
              />
            </div>
            {/* <div className="col-12 col-md-6 mb-3">
              <Label label="Balance" isRequired />
              <Input value={formData.balance} onChange={(e) => onFormChange('balance', e.target.value)} className="form-control error-balance" name="balance" type="number" placeholder="Enter balance" />
            </div> */}
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('description')} />
              <Input
                value={formData.description}
                onChange={(e) => onFormChange('description', e.target.value)}
                className="form-control error-description"
                name="description"
                placeholder={t('enter_description')}
              />
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text="Cancel" color="light" width="sm" onClick={() => onCancel()} />
            <Button text="Create" type="submit" width="sm" isLoading={isFormProcessing} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default ChartOfAccountsCreate;
