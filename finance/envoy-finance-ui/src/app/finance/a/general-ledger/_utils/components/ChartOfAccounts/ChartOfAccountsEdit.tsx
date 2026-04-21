import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { FormEvent, useEffect, useState } from 'react';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { useTrans } from '@/helpers/services/lang/langService';
import { initFormData } from '../../model';
import { clearError } from '@/helpers/handlers/validationErrorHandler';
import { getOnechartOfAccounts, updatechartOfAccounts } from '../../api-service';
import { Select } from '@apptimus-ui/select';

export const ChartOfAccountsEdit = ({ isOpen, editId, afterUpdate, onCancel }: { isOpen: boolean; editId: string; onCancel: Function; afterUpdate: Function }) => {
  const t = useTrans('label.general_ledger,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);
  const [skeleton, setSkeleton] = useState(true);

  const accountTypeOptions = [
    { label: 'Asset', value: 'asset' },
    { label: 'Liability', value: 'liability' },
    { label: 'Equity', value: 'equity' },
    { label: 'Revenue', value: 'revenue' },
    { label: 'Expense', value: 'expense' },
  ];

  console.log(
    accountTypeOptions.find((opt) => opt.value === formData.account_type),
    'efvewfvwefc',
  );

  const selectedAccountType = accountTypeOptions.find((opt) => opt.value === formData.account_type);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOnechartOfAccounts(editId);

      if (responseData?.is_success) {
        const { account_name, account_type, description } = responseData.result;
        setFormData({ account_name, account_type, description });
        setSkeleton(false);
      }
    };

    if (editId) {
      setSkeleton(true);
      fetchData();
    }
  }, [editId]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.chart_of_accounts_crud.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updatechartOfAccounts(editId, formData);
      setIsFormProcessing(false);
      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setFormData(initFormData);
        onCancel();
        afterUpdate();
      }
    } catch (error) {
      console.error('An error occurred:', error);
      setIsFormProcessing(false);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('edit_entity', { entity: t('chart_of_accounts') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.chart_of_accounts_crud.update}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('account_name')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.account_name}
                  onChange={(e) => onFormChange('account_name', e.target.value)}
                  className="form-control error-account_name"
                  name="account_name"
                  placeholder={t('enter_account_name')}
                />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('account_type')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Select
                  onChange={(_e, data) => onFormChange('account_type', data?.value || '')}
                  options={accountTypeOptions}
                  option={{ label: 'label', value: 'value' }}
                  isSearchable={false}
                  className="form-control error-account_type"
                  defaultValue={selectedAccountType ? selectedAccountType : {}}
                  placeholder={t('select_account_type')}
                />
              )}
            </div>
            {/* <div className="col-12 col-md-6 mb-3">
              <Label label="Balance" isRequired />
              {skeleton ? <InputSkeleton /> : (
                <Input value={formData.balance} onChange={(e) => onFormChange('balance', e.target.value)} className="form-control error-balance" name="balance" type="number" placeholder="Enter balance" />
              )}
            </div> */}
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('description')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.description}
                  onChange={(e) => onFormChange('description', e.target.value)}
                  className="form-control error-description"
                  name="description"
                  placeholder={t('enter_description')}
                />
              )}
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('update')} type="submit" width="sm" isLoading={isFormProcessing} disabled={skeleton} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
};
