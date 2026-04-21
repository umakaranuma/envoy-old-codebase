import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button, Input, Label, Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import PhoneInput from 'react-phone-input-2';
import 'react-phone-input-2/lib/style.css';
import { createPolicyHolder, getMyselfInfo, getOnePolicyHolderInfo } from '../../../../api-service';
import { initPolicyHolderInfo } from '../../../../model';
import { Select } from '@apptimus-ui/select';

function PolicyHolderInfo({ setToggleTab, requestId, onBack, type }: { setToggleTab: Function; requestId: string | null; onBack: Function; type: string }) {
  const t = useTrans('label.my_policy,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [formData, setFormData] = useState(initPolicyHolderInfo);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [skeleton, setSkeleton] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOnePolicyHolderInfo(requestId as string);
      if (responseData?.is_success) {
        setFormData(responseData.result);
        setSkeleton(false);
      }

      if (responseData.status_code === 404) {
        setSkeleton(false);
      }
    };
    if (requestId) {
      setSkeleton(true);
      fetchData();
    }
  }, [requestId]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    clearError(form.policy_holder_info.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createPolicyHolder({ ...formData, customer_request_id: requestId, type: type });
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.policy_holder_info.store, tBe);
      }

      if (responseData.is_success) {
        setToggleTab('coverage_info');
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  const handleBuyingForMyself = async (e: React.ChangeEvent<HTMLInputElement>) => {
    clearError(form.policy_holder_info.store);
    if (e.target.checked) {
      setSkeleton(true);
      try {
        const responseData = await getMyselfInfo();
        setIsFormProcessing(false);

        if (responseData.is_success) {
          setFormData({
            policy_holder_name: responseData.result.name,
            date_of_birth: '',
            gender: '',
            nic: '',
            phone_number: responseData.result.phone_number,
            email: responseData.result.email,
            address: responseData.result.address,
            contact_method: '',
            is_myself: false,
          });
          onFormChange('is_myself', e.target.checked);
          setSkeleton(false);
        }
      } catch (error) {
        console.error('An error occurred:', error);
      }
    } else {
      setFormData(initPolicyHolderInfo);
      onFormChange('is_myself', e.target.checked);
    }
  };

  return (
    <>
      <div className="mb-4">
        <form onSubmit={onSubmit} id={`${form.policy_holder_info.store}`}>
          <div className="panel-title">{t('policyholder_information')}</div>
          {skeleton ? (
            <Skeleton height="200px" width="100%" />
          ) : (
            <div className="row">
              <div className="d-flex flex-row gap-3 mb-3">
                <Label label={t('buying_for_myself')} />
                <input type="checkbox" className="mb-2" onChange={(e) => handleBuyingForMyself(e)} checked={formData.is_myself} />
              </div>
              <div className="col-12 col-md-6 mb-3">
                <Input
                  isRequired
                  label={t('policyholder_name')}
                  value={formData.policy_holder_name}
                  onChange={(e) => onFormChange('policy_holder_name', e.target.value)}
                  className="form-control error-policy_holder_name"
                  name="policy_holder_name"
                />
              </div>
              <div className="col-12 col-md-6 mb-3">
                <Input
                  isRequired
                  type="date"
                  label={t('date_of_birth')}
                  value={formData.date_of_birth}
                  onChange={(e) => onFormChange('date_of_birth', e.target.value)}
                  className="form-control error-date_of_birth"
                  name="date_of_birth"
                />
              </div>
              <div className="col-12 col-md-4 mb-3 custom-select">
                <Label label={t('gender')} isRequired />
                <Select
                  onChange={(value) => onFormChange('gender', value)}
                  className="form-control error-gender"
                  option={{ label: 'label', value: 'value' }}
                  options={[
                    { label: 'Male', value: 'Male' },
                    { label: 'Female', value: 'Female' },
                    { label: 'Non-binary', value: 'Non-binary' },
                    { label: 'Rather not say', value: 'Rather not say' },
                  ]}
                  defaultValue={{ label: formData.gender, value: formData.gender }}
                />
              </div>
              <div className="col-12 col-md-4 mb-3">
                <Input isRequired label={t('nic_number')} value={formData.nic} onChange={(e) => onFormChange('nic', e.target.value)} className="form-control error-nic" name="nic" />
              </div>
              <div className="col-12 col-md-4 mb-3">
                <Label label={t('phone_number')} isRequired />
                <PhoneInput
                  country={'lk'}
                  enableAreaCodes={true}
                  value={formData.phone_number}
                  inputStyle={{ height: '40px', width: '100%' }}
                  containerStyle={{ height: '40px', width: '100%' }}
                  onChange={(phone) => onFormChange('phone_number', phone)}
                  inputClass="form-control error-phone_number"
                  countryCodeEditable={false}
                />
              </div>
              <div className="col-12 col-md-4 mb-3">
                <Input isRequired label={t('email_address')} value={formData.email} onChange={(e) => onFormChange('email', e.target.value)} className="form-control error-email" name="email" />
              </div>
              <div className="col-12 col-md-4 mb-3">
                <Input
                  isRequired
                  label={t('residential_address')}
                  value={formData.address}
                  onChange={(e) => onFormChange('address', e.target.value)}
                  className="form-control error-address"
                  name="address"
                />
              </div>
              <div className="col-12 col-md-4 mb-3 custom-select">
                <Label label={t('preferred_contact_method')} isRequired />
                <Select
                  onChange={(value) => onFormChange('contact_method', value)}
                  className="form-control error-contact_method"
                  option={{ label: 'label', value: 'value' }}
                  options={[
                    { label: 'Phone', value: 'Phone' },
                    { label: 'Email', value: 'Email' },
                    { label: 'SMS', value: 'SMS' },
                  ]}
                  defaultValue={{ label: formData.contact_method, value: formData.contact_method }}
                />
              </div>
            </div>
          )}
        </form>
      </div>
      <div className="d-flex justify-content-start gap-2 mt-3">
        <Button color="light" className="d-flex align-items-center gap-1" onClick={() => onBack()}>
          <Flexicon icon="chevron-left" variant="line" size={18} />
          <span className="d-none d-sm-inline">{t('back')}</span>
        </Button>
        <Button color="primary" className="d-flex align-items-center gap-1" type="submit" onClick={onSubmit} isLoading={isFormProcessing || skeleton}>
          <span className="d-none d-sm-inline">{t('next')}</span>
          <Flexicon icon="chevron-right" variant="line" size={18} />
        </Button>
      </div>
    </>
  );
}

export default PolicyHolderInfo;
