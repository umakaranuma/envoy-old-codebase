import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { AsyncSelect } from '@apptimus-ui/select';
import { Button, Label } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import { fetchAllInterestedProducts, fetchAllRiskTypes } from '../../../service';
import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { getNewPolicyFormTemplate } from '@/components/others/common/form/api-service';

function SelectInterestedProduct({ isOpen, onCancel, setIds, type }: { isOpen: boolean; onCancel: Function; setIds: Function; type: string }) {
  const t = useTrans('label.my_policy,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({ risk_type: '', interested_product: '' });
  const [error, setError] = useState('');
  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    clearError(form.select_interested_product.store);
    setError('');
    const error: { [key: string]: Array<{ error_type: string; tokens: { _attribute: string } }> } = {};
    if (!formData.risk_type) {
      error['risk_type'] = [
        {
          error_type: 'required',
          tokens: {
            _attribute: 'risk_type',
          },
        },
      ];
    }

    if (!formData.interested_product) {
      error['interested_product'] = [
        {
          error_type: 'required',
          tokens: {
            _attribute: 'interested_product',
          },
        },
      ];
    }

    if (Object.keys(error).length > 0) {
      printError(error, form.select_interested_product.store, tBe);
    } else {
      try {
        setIsFormProcessing(true);
        const responseData = await getNewPolicyFormTemplate(formData.risk_type, 'onboarding');
        setIsFormProcessing(false);
        if (responseData.system_code === 'NOT_FOUND') {
          setError(responseData.message);
          return;
        }
        if (responseData.is_success) {
          setIds(responseData.result.template.id, formData.interested_product, formData.risk_type);
        }
      } catch (error) {
        console.error('An error occurred:', error);
      }
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={type === 'customer_policy' ? t('request_new_policy') : t('request_new_quotation')} onClose={() => onCancel()} />
      <ModalBody>
        <div className="row" id={`${form.select_interested_product.store}`}>
          {type === 'customer_policy' && <div className="fs-13 text-muted mb-3">{t('to_get_started_choose_the_type_of_policy_you_are_interested_in')}</div>}
          <div className="col-12 mb-3 custom-select">
            <Label label={t('risk_type')} isRequired />
            <AsyncSelect
              onChange={(value) => {
                onFormChange('risk_type', value);
                onFormChange('interested_product', '');
              }}
              className="form-control error-risk_type"
              option={{ label: 'title', value: 'id' }}
              isSearchable={true}
              loadOptions={(searchValue: any, currentPage: any) => fetchAllRiskTypes(searchValue, currentPage)}
            />
          </div>
          {formData.risk_type && (
            <div className="col-12 mb-3 custom-select" key={`risk-${formData.risk_type}`}>
              <Label label={t('interested_product')} isRequired />
              <AsyncSelect
                onChange={(value) => onFormChange('interested_product', value)}
                className="form-control error-interested_product"
                option={{ label: 'name', value: 'id' }}
                isSearchable={false}
                loadOptions={(searchValue: any, currentPage: any) => fetchAllInterestedProducts(searchValue, currentPage, formData.risk_type)}
              />
            </div>
          )}
        </div>
        {error && <span className="custom-error">{tBe(error)}</span>}
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          <Button text={t('continue')} type="submit" width="sm" isLoading={isFormProcessing} onClick={onSubmit} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default SelectInterestedProduct;
