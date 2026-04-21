import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { AsyncSelect } from '@apptimus-ui/select';
import { Button, Label } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useRouter } from 'next/navigation';
import { fetchAllIssuedPolicies } from '@/app/policy/a/issued-policies/_utils/service';
import CustomerCard from '@/components/others/page-related/CustomerCard';
import { fetchAllCustomers, fetchAllOpportunities } from '../../services';
import 'react-phone-input-2/lib/style.css';
import PolicyCard from '@/components/others/page-related/PolicyCard';
import { INewCustomerInfo } from '../../model';
import { hexToRgba } from '@/helpers/services/commonService';

function SelectPolicyRequestType({
  isOpen,
  onCancel,
  issuedPolicy = false,
  handleOpenCreateCustomer,
  newCustomerInfo,
}: {
  isOpen: boolean;
  onCancel: Function;
  issuedPolicy?: boolean;
  handleOpenCreateCustomer: Function;
  newCustomerInfo: INewCustomerInfo | null;
}) {
  const t = useTrans('label.policy_request,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({
    is_renewal: 0,
    policy_id: '',
    customer_id: '',
    customer_name: '',
    customer_primary_contact: '',
    customer_email: '',
    customer_address: '',
    lead_id: '',
    customer_type: null,
    transaction_type: null,
  });
  const router = useRouter();
  const [defaultCustomer, setDefaultCustomer] = useState<INewCustomerInfo | null>(newCustomerInfo);
  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  useEffect(() => {
    if (newCustomerInfo) {
      onFormChange('customer_id', newCustomerInfo.id);
      onFormChange('customer_name', newCustomerInfo.name);
      onFormChange('customer_primary_contact', newCustomerInfo.primary_contact || '');
      onFormChange('customer_email', newCustomerInfo.email || '');
      onFormChange('customer_type', null);
    }
  }, [newCustomerInfo]);

  async function onSubmit() {
    clearError(form.policy_request.store);
    const error: { [key: string]: Array<{ error_type: string; tokens: { _attribute: string } }> } = {};
    if (formData.is_renewal !== 0 && !formData.is_renewal) {
      error['is_renewal'] = [
        {
          error_type: 'required',
          tokens: {
            _attribute: 'is_renewal',
          },
        },
      ];
    }

    if (formData.is_renewal === 1 && !formData.lead_id && !formData.policy_id) {
      error['policy_id'] = [
        {
          error_type: 'required',
          tokens: {
            _attribute: 'policy_id',
          },
        },
      ];
    }

    if (formData.is_renewal === 0 && formData.customer_id === '') {
      error['customer_id'] = [
        {
          error_type: 'required',
          tokens: {
            _attribute: 'customer_id',
          },
        },
      ];
    }

    if (Object.keys(error).length > 0) {
      console.log(error);

      printError(error, form.policy_request.store, tBe);
    } else {
      setIsFormProcessing(true);
      router.push(
        `/policy/a/policy-request/create?ip=${issuedPolicy}&cusId=${formData.customer_id}&ct=${formData.customer_type}&is_renewal=${formData.is_renewal === 1 ? 'true' : 'false'}&policyId=${formData.policy_id}&leadId=${formData.lead_id}`,
      );
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={issuedPolicy ? t('create_policy') : t('create_policy_request')} onClose={() => onCancel()} />
      <ModalBody>
        <div className="row" id={`${form.policy_request.store}`}>
          {/* {formData.is_renewal === 0 && ( */}
          <div className="col-12 mb-3 custom-select">
            <Label label={t('select_customer')} isRequired />
            <AsyncSelect
              onChange={(_value, data) => {
                setDefaultCustomer(null);
                onFormChange('customer_id', data.id), onFormChange('customer_name', data.name);
                onFormChange('customer_primary_contact', data.primary_contact_number || '');
                onFormChange('customer_email', data.primary_contact_email || '');
                onFormChange('customer_address', data.primary_contact_address || '');
                onFormChange('customer_type', data.type === 'Corporate' ? 1 : 0);
                onFormChange('transaction_type', null);
                onFormChange('is_renewal', 0);
              }}
              className="form-control error-customer_id"
              option={{
                labelFn: (option) => <CustomerCard name={option.name} picture={option.picture} contactNumber={option.primary_contact_number} contactEmail={option.primary_contact_email} />,
                label: 'name',
                value: 'id',
              }}
              isSearchable={true}
              creatable={{
                visible: true,
                position: 'top',
                action: () => {
                  handleOpenCreateCustomer();
                },
              }}
              defaultValue={
                defaultCustomer
                  ? { name: defaultCustomer.name, primary_contact_number: defaultCustomer.primary_contact, primary_contact_email: defaultCustomer.email, picture: '', id: defaultCustomer.id }
                  : {}
              }
              loadOptions={(searchValue: any, currentPage: any) => fetchAllCustomers(searchValue, currentPage)}
            />
          </div>
          {/* )} */}
          {formData.customer_id !== '' && (
            <div className={`col-12 mb-3 custom-select`} key={`lead-${formData.customer_id}`}>
              <Label htmlFor="select_lead" label={t('select_lead')} />
              <AsyncSelect
                onChange={(value, data) => {
                  onFormChange('lead_id', value);
                  if (data.transaction_type) {
                    if (data.transaction_type === 'new') {
                      onFormChange('is_renewal', 0);
                    } else if (data.transaction_type === 'renewal') {
                      onFormChange('is_renewal', 1);
                    }
                  }
                  onFormChange('transaction_type', data.transaction_type);
                }}
                loadOptions={(searchValue: any, currentPage: any) => fetchAllOpportunities(searchValue, currentPage, formData.customer_id)}
                option={{
                  labelFn: (option) => (
                    <>
                      <div className="text">{option.title}</div>
                      <div className="d-flex align-items-center gap-2 mt-1">
                        <div
                          className={'rounded-5 fw-semibold badge error-lead_id'}
                          style={{ background: hexToRgba(option.stage_color, 0.1), border: `1px solid ${hexToRgba(option.stage_color, 0.4)}`, color: option.stage_color }}
                        >
                          {option.stage_name}
                        </div>
                        <div className="text-muted">|</div>
                        <div className="text">{option.code}</div>
                      </div>
                    </>
                  ),
                  label: 'title',
                  value: 'id',
                }}
                isSearchable={true}
                // creatable={{
                //   visible: true,
                //   position: 'top',
                //   action: () => {
                //     handleCreateLead();
                //   },
                // }}
                className="form-control error-lead_id"
              />
            </div>
          )}
          <div className="col-12 mb-2" key={`type-${formData.customer_id}`}>
            <Label htmlFor="requested_type" label={t('requested_type')} isRequired />
            <div className="d-flex flex-row gap-2 align-items-center">
              <input
                type="radio"
                disabled={formData.transaction_type === 'renewal'}
                id="new"
                name="requested_type"
                value="new"
                checked={formData.is_renewal === 0}
                className="mb-2"
                onChange={() => {
                  // onFormChange('transaction_type', 'new');
                  onFormChange('is_renewal', 0);
                }}
              />
              <Label htmlFor="new" label={t('new_policy')} />

              <input
                type="radio"
                disabled={formData.transaction_type === 'new'}
                id="renew"
                name="requested_type"
                value="renew"
                checked={formData.is_renewal === 1}
                className="mb-2"
                onChange={() => {
                  // onFormChange('transaction_type', 'renewal');
                  onFormChange('is_renewal', 1);
                }}
              />
              <Label htmlFor="renew" label={t('renew_policy')} />
            </div>
          </div>
          {formData.is_renewal === 1 && !formData.lead_id && (
            <div className="col-12 mb-3 custom-select custom-values" key={`policy-${formData.customer_id}`}>
              <Label label={t('select_policy')} isRequired />
              <AsyncSelect
                onChange={(value, data) => {
                  onFormChange('policy_id', value);
                  onFormChange('customer_id', data.customer_id);
                }}
                className="form-control error-policy_id custom-container"
                // option={{ label: 'brokerage_policy_id', value: 'id' }}
                isSearchable={true}
                option={{
                  labelFn: (option) => (
                    <PolicyCard
                      premiumAmount={option.premium_amount}
                      status={option.status}
                      startDate={option.start_date}
                      endDate={option.end_date}
                      policyNumber={option.brokerage_policy_id}
                      productName={option.product}
                    />
                  ),
                  label: 'brokerage_policy_id',
                  value: 'policy_base_id',
                }}
                loadOptions={(searchValue: any, currentPage: any) => fetchAllIssuedPolicies(searchValue, currentPage, formData.customer_id)}
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

export default SelectPolicyRequestType;
