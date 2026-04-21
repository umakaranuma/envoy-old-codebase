import { useState, FormEvent, useEffect } from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllCurrency, fetchallNativeProducts, fetchAllTeamsDropdown } from '../../services';
import { initProductGroup } from '../../modal';
import { form } from '@/constans/Form';
import { createProductGroups } from '../../api-service';
import { useCurrency } from '@/contexts/CurrencyContext';

export const ProductGroupCreate = ({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: () => void; afterSave: () => void }) => {
  const t = useTrans('label.products,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [formData, setFormData] = useState(initProductGroup);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const { currency } = useCurrency();

  useEffect(() => {
    onFormChange('currency_id', currency.id);
    onFormChange('currency_code', currency.code);
  }, [currency]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.product.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createProductGroups(formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.product.store, tBe);
      }

      if (responseData.is_success) {
        afterSave();
        setFormData(initProductGroup);
        onCancel();
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen} onBackdrop={onCancel}>
      <ModalHeader title={t('add_new_entity', { entity: t('product_group') })} onClose={onCancel} />
      <form onSubmit={onSubmit} id={`${form.product.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              <Label label={t('group_name')} isRequired />
              <Input
                type="text"
                name="name"
                value={formData?.name}
                onChange={(e) => {
                  onFormChange('name', e.target.value);
                }}
                className="form-control error-name"
              />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="currency" label={t('currency')} isRequired />
              <AsyncSelect
                onChange={(_value, data) => {
                  onFormChange('currency_id', data.id);
                  onFormChange('currency_code', data.code);
                }}
                className="form-control error-currency_id"
                option={{ label: 'code', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllCurrency(searchValue, currentPage)}
                defaultValue={{ id: formData.currency_id, code: formData.currency_code }}
              />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('products')} isRequired />
              <AsyncSelect
                onChange={(value) => {
                  onFormChange('product_ids', value);
                }}
                className="form-control error-product_ids"
                option={{ label: 'name', value: 'id' }}
                isSearchable={true}
                loadOptions={fetchallNativeProducts}
                multiple
              />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('teams')} isRequired />
              <AsyncSelect
                onChange={(value) => {
                  onFormChange('team_ids', value);
                }}
                className="form-control error-team_ids"
                option={{ label: 'name', value: 'id' }}
                isSearchable={true}
                loadOptions={fetchAllTeamsDropdown}
                multiple
              />
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('create')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={onCancel} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
};
