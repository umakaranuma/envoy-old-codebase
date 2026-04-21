import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { AsyncSelect } from '@apptimus-ui/select';
import { Button, Label } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useRouter } from 'next/navigation';
import { fetchAllCustomers, fetchAllLeadsByCustomer, fetchAllRiskTypesByLead } from '../services';

function SelectRiskData({ isOpen, onCancel }: { isOpen: boolean; onCancel: Function }) {
  const t = useTrans('label.risk_register,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({ customer_id: '', lead_id: '', risk_type_id: '' });
  const router = useRouter();

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    clearError(form.select_risk_data.store);
    const error: { [key: string]: Array<{ error_type: string; tokens: { _attribute: string } }> } = {};
    if (!formData.customer_id) {
      error['customer_id'] = [
        {
          error_type: 'required',
          tokens: {
            _attribute: 'customer_id',
          },
        },
      ];
    }

    // if (!formData.lead_id) {
    //   error['lead_id'] = [
    //     {
    //       error_type: 'required',
    //       tokens: {
    //         _attribute: 'lead_id',
    //       },
    //     },
    //   ];
    // }

    if (!formData.risk_type_id) {
      error['risk_type_id'] = [
        {
          error_type: 'required',
          tokens: {
            _attribute: 'risk_type_id',
          },
        },
      ];
    }

    if (Object.keys(error).length > 0) {
      printError(error, form.select_risk_data.store, tBe);
    } else {
      setIsFormProcessing(true);
      router.push(`/policy/a/risk-register/create?cId=${formData.customer_id}&lId=${formData.lead_id}&rId=${formData.risk_type_id}`);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('add_new_risk_details')} onClose={() => onCancel()} />
      <ModalBody>
        <div className="row" id={`${form.select_risk_data.store}`}>
          <div className="col-12 mb-3 custom-select">
            <Label label={t('customer')} isRequired />
            <AsyncSelect
              onChange={(value) => onFormChange('customer_id', value)}
              className="form-control error-customer_id"
              option={{ label: 'name', value: 'id' }}
              isSearchable={false}
              loadOptions={(searchValue: any, currentPage: any) => fetchAllCustomers(searchValue, currentPage)}
              creatable={{
                visible: true,
                position: 'top',
                action: () => {
                  router.push(`/a/accounts`);
                },
              }}
            />
          </div>
          {formData.customer_id && (
            <div className={`col-12 mb-3 custom-select`} key={`lead-${formData.customer_id}`}>
              <Label htmlFor="select_lead" label={t('select_lead')} />
              <AsyncSelect
                onChange={(_value, data) => {
                  onFormChange('lead_id', data.id);
                }}
                loadOptions={(searchValue: any, currentPage: any) => fetchAllLeadsByCustomer(searchValue, currentPage, formData.customer_id)}
                option={{
                  labelFn: (option) => (
                    <>
                      <div className="text">{option.title}</div>
                      <div className="d-flex align-items-center gap-2 mt-1">
                        {/* <div
                        className={'rounded-5 fw-semibold badge error-lead_id'}
                        style={{ background: hexToRgba(option.stage_color, 0.1), border: `1px solid ${hexToRgba(option.stage_color, 0.4)}`, color: option.stage_color }}
                      >
                        {option.stage_name}
                      </div> */}
                        <div className="text-muted">|</div>
                        <div className="text">{option.code}</div>
                      </div>
                    </>
                  ),
                  label: 'title',
                  value: 'id',
                }}
                className="form-control error-lead_id"
              />
            </div>
          )}
          {formData.customer_id && (
            <div className="col-12 mb-3 custom-select" key={`risk_type-${formData.lead_id || formData.customer_id}`}>
              <Label label={t('risk_type')} isRequired />
              <AsyncSelect
                onChange={(value) => onFormChange('risk_type_id', value)}
                className="form-control error-risk_type_id"
                option={{ label: 'name', value: 'id' }}
                isSearchable={false}
                loadOptions={(searchStr: string, page: number) => fetchAllRiskTypesByLead(searchStr, page, formData.lead_id)}
              />
            </div>
          )}
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          <Button text={t('next')} type="submit" width="sm" isLoading={isFormProcessing} onClick={onSubmit} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default SelectRiskData;
