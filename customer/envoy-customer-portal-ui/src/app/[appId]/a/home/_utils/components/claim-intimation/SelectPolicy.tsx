import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { AsyncSelect } from '@apptimus-ui/select';
import { Button, Label, Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { fetchAllIssuedPolicies, fetchAllRiskTypesByPolicyBase } from '../../service';
import { useParams, useRouter } from 'next/navigation';
import PolicyCard from './PolicyCard';
import RiskTypeList from './RiskTypeList';
import { IElement } from '@/components/others/common/form/template-modal';
import { getFormsOfCustomer, getNewPolicyFormTemplate } from '@/components/others/common/form/api-service';
import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';

function SelectPolicy({ isOpen, onCancel }: { isOpen: boolean; onCancel: Function }) {
  const t = useTrans('label.home,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({ brokerage_policy_id: '', policy_base_id: '', risk_type_id: '', customer_id: '', customer_type: '', risk_info_ids: [] });
  const router = useRouter();
  const params = useParams();
  const appId = params.appId as string;
  const [tableElements, setTableElements] = useState<IElement[]>([]);
  const [loading, setLoading] = useState(false);
  const authUser = getLocalStorage(local_storage.auth_user_info);

  useEffect(() => {
    onFormChange('customer_type', authUser?.type || '');
    onFormChange('customer_id', authUser?.id || '');
  }, []);

  useEffect(() => {
    console.log('formData:', formData);
  }, [formData]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    clearError(form.select_policy.store);
    const error: { [key: string]: Array<{ error_type: string; tokens: { _attribute: string } }> } = {};
    if (!formData.brokerage_policy_id) {
      error['brokerage_policy_id'] = [
        {
          error_type: 'required',
          tokens: {
            _attribute: 'brokerage_policy_id',
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
      printError(error, form.select_policy.store, tBe);
    } else {
      setIsFormProcessing(true);
      router.push(`/${appId}/a/home/claim-intimation?pid=${formData.brokerage_policy_id}&rIds=${formData.risk_info_ids.join(',') || ''}`);
    }
  }

  useEffect(() => {
    const fetchData = async () => {
      try {
        const responseData = await getNewPolicyFormTemplate(formData.risk_type_id, 'ONBOARDING');
        if (responseData?.is_success) {
          const response = await getFormsOfCustomer(responseData.result.template.id || '');
          setTableElements(response?.result.elements || []);
          setLoading(false);
        }
      } catch (error) {
        console.error('Error fetching form attributes:', error);
      }
    };

    if (formData.risk_type_id) {
      fetchData();
    }
  }, [formData.risk_type_id, formData.policy_base_id]);

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('report_a_claim')} onClose={() => onCancel()} />
      <ModalBody>
        <div className="row" id={`${form.select_policy.store}`}>
          {/* <div className="col-12 mb-3 custom-select">
            <Label label={t('select_policy')} isRequired />
            <AsyncSelect
              onChange={(value) => onFormChange('brokerage_policy_id', value)}
              className="form-control error-brokerage_policy_id"
              option={{ label: 'brokerage_policy_id', value: 'id' }}
              isSearchable={false}
              loadOptions={(searchValue: any, currentPage: any) => fetchAllIssuedPolicies(searchValue, currentPage)}
            />
          </div> */}
          <div className="col-12 mb-3 custom-select">
            <Label label={t('select_policy')} isRequired />
            <AsyncSelect
              onChange={(value, data) => {
                onFormChange('brokerage_policy_id', value);
                onFormChange('policy_base_id', data?.policy_base_id);

                if (formData.customer_type === 'Personal') {
                  onFormChange('risk_type_id', data?.risk_type_id);
                }
              }}
              className="form-control error-brokerage_policy_id"
              isSearchable={true}
              option={{
                labelFn: (option) => (
                  <PolicyCard
                    name={option.customer_name}
                    picture={option.picture}
                    contactNumber={option.customer_primary_contact}
                    contactEmail={option.customer_email}
                    riskType={option.risk_type_name}
                    policyNumber={option.brokerage_policy_id}
                    productName={option.product}
                  />
                ),
                label: 'brokerage_policy_id',
                value: 'id',
              }}
              loadOptions={(searchValue: any, currentPage: any) => fetchAllIssuedPolicies(searchValue, currentPage)}
            />
          </div>
          {formData.policy_base_id && formData.customer_type === 'Corporate' && (
            <div className="col-12 mb-3 custom-select" key={`policy-${formData.policy_base_id}`}>
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
          {formData.risk_type_id && (
            <div className="col-12 mb-3" key={`risk-${formData.risk_type_id || formData.policy_base_id}`}>
              <Label label={t('risk_info')} isRequired />
              {!loading && tableElements.length > 0 ? (
                <RiskTypeList
                  customerId={formData.customer_id}
                  policyBaseId={formData.policy_base_id}
                  riskTypeId={formData.risk_type_id}
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
          <Button text={t('continue')} type="submit" width="sm" isLoading={isFormProcessing} onClick={onSubmit} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default SelectPolicy;
