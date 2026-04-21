import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { AsyncSelect } from '@apptimus-ui/select';
import { Button, Label, Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useRouter } from 'next/navigation';
import { fetchAllCustomers, fetchAllRiskTypesByPolicyBase } from '@/app/policy/a/risk-register/_utils/services';
import CustomerCard from '@/components/others/page-related/CustomerCard';
import { fetchPoliciesOfCustomer } from '../../services';
import { IElement } from '@/components/others/common/form/template-modal';
import RiskTypeList from './RiskTypeList';
import { getAllOpportunityTypeFormAttributes } from '@/components/others/common/lead/api-service';
import { getAllOpportunityTypeFormElements } from '@/components/others/common/risk-type-view/api-service';
import PolicyCard from '@/components/others/page-related/PolicyCard';

function SelectPolicyDetails({ isOpen, onCancel }: { isOpen: boolean; onCancel: Function }) {
  const t = useTrans('label.claim,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({ customer_id: '', policy_id: '', policy_base_id: '', risk_type_id: '', customer_type: '', risk_info_ids: [] });
  const [tableElements, setTableElements] = useState<IElement[]>([]);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  useEffect(() => {
    console.log('formData', formData);
  }, [formData]);

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

    if (!formData.policy_id) {
      error['policy_id'] = [
        {
          error_type: 'required',
          tokens: {
            _attribute: 'policy_id',
          },
        },
      ];
    }

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

    if (formData.risk_info_ids.length === 0) {
      error['risk_info_ids'] = [
        {
          error_type: 'required',
          tokens: {
            _attribute: 'risk_info_ids',
          },
        },
      ];
    }

    if (Object.keys(error).length > 0) {
      printError(error, form.select_risk_data.store, tBe);
    } else {
      setIsFormProcessing(true);
      router.push(`/policy/a/claim/create?t=policy_info&pid=${formData.policy_id}&rid=${formData.risk_type_id}&infoId=${formData.risk_info_ids.join(',')}`);
    }
  }

  useEffect(() => {
    const fetchData = async () => {
      try {
        const responseData = await getAllOpportunityTypeFormAttributes(formData.risk_type_id, 'ONBOARDING');
        if (responseData?.is_success) {
          const response = await getAllOpportunityTypeFormElements(responseData.result.form_id || '');
          setTableElements(response?.result || []);
          setLoading(false);
        }
      } catch (error) {
        console.error('Error fetching form attributes:', error);
      }
    };

    if (formData.risk_type_id) {
      fetchData();
    }
  }, [formData.risk_type_id]);

  return (
    <Modal isOpen={isOpen} size="lg">
      <ModalHeader title={t('new_claim_request')} onClose={() => onCancel()} />
      <ModalBody>
        <div className="row" id={`${form.select_risk_data.store}`}>
          <div className="col-12 col-md-6 mb-3 custom-select">
            <Label label={t('customer')} isRequired />
            <AsyncSelect
              onChange={(value, data) => {
                onFormChange('customer_id', value);
                onFormChange('customer_type', data.type);
              }}
              className="form-control error-customer_id"
              isSearchable={true}
              option={{
                labelFn: (option) => <CustomerCard name={option.name} picture={option.picture} contactNumber={option.primary_contact_number} contactEmail={option.primary_contact_email} />,
                label: 'name',
                value: 'id',
              }}
              loadOptions={(searchValue: any, currentPage: any) => fetchAllCustomers(searchValue, currentPage)}
            />
          </div>
          {formData.customer_id && (
            <div className={`col-12 col-md-6 mb-3 custom-select custom-values`} key={`customer-${formData.customer_id}`}>
              <Label label={t('policy')} isRequired />
              <AsyncSelect
                onChange={(_value, data) => {
                  onFormChange('policy_base_id', data.policy_base_id);
                  onFormChange('policy_id', data.id);
                  if (formData.customer_type === 'Personal') {
                    onFormChange('risk_type_id', data.risk_type_id);
                  }
                }}
                loadOptions={(searchValue: any, currentPage: any) => fetchPoliciesOfCustomer(searchValue, currentPage, formData.customer_id)}
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
                className="form-control error-policy_id custom-container"
              />
            </div>
          )}
          {formData.policy_base_id && formData.customer_type === 'Corporate' && (
            <div className="col-12 col-md-6 mb-3 custom-select" key={`policy-${formData.policy_base_id}-${formData.customer_id}`}>
              <Label label={t('risk_type')} isRequired />
              <AsyncSelect
                onChange={(value) => onFormChange('risk_type_id', value)}
                className="form-control error-risk_type_id"
                option={{ label: 'title', value: 'id' }}
                isSearchable={false}
                loadOptions={(searchStr: string, page: number) => fetchAllRiskTypesByPolicyBase(searchStr, page, formData.policy_base_id)}
              />
            </div>
          )}
          {formData.risk_type_id && formData.policy_base_id && (
            <div className="col-12 mb-3" key={`risk-${formData.customer_id}-${formData.policy_base_id}-${formData.risk_type_id}`}>
              <Label label={t('risk_info')} isRequired />
              {!loading && tableElements.length > 0 ? (
                <RiskTypeList
                  policyBaseId={formData.policy_base_id}
                  riskTypeId={formData.risk_type_id}
                  customerId={formData.customer_id}
                  tableElements={tableElements}
                  selectedRiskInfoIds={(ids) => onFormChange('risk_info_ids', ids)}
                />
              ) : (
                <Skeleton width="100%" height="100px" />
              )}
              <span className="error-risk_info_ids"></span>
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

export default SelectPolicyDetails;
