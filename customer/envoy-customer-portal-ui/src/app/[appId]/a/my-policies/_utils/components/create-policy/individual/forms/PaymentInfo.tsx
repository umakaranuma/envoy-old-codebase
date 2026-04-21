import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Select } from '@apptimus-ui/select';
import { Button, Input, Label, Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { createPaymentInfo, getOnePaymentInfo } from '../../../../api-service';

function PaymentInfo({ setToggleTab, requestId, type }: { setToggleTab: Function; requestId: string | null; type: string }) {
  const t = useTrans('label.my_policy,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [formData, setFormData] = useState({
    payment_method: '',
    payment_frequency: '',
    bank_name: '',
    branch: '',
    account_holder_name: '',
    bank_number: '',
    iban_swift_code: '',
    estimated_amount: '',
  });
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [skeleton, setSkeleton] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOnePaymentInfo(requestId as string);
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
    clearError(form.payment_info.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createPaymentInfo({ ...formData, request_id: requestId, type: type });
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.payment_info.store, tBe);
      }

      if (responseData.is_success) {
        setToggleTab('supporting_documents');
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <>
      <div className="mb-4">
        <form onSubmit={onSubmit} id={`${form.payment_info.store}`}>
          <div className="panel-title">{t('payment_information')}</div>
          {skeleton ? (
            <Skeleton height="200px" width="100%" />
          ) : (
            <div className="row">
              <div className="col-12 col-md-4 mb-3 custom-select">
                <Label label={t('payment_method')} isRequired />
                <Select
                  onChange={(value) => onFormChange('payment_method', value)}
                  className="form-control error-payment_method"
                  option={{ label: 'label', value: 'value' }}
                  isSearchable={true}
                  options={[
                    { label: 'Bank Transfer', value: 'Bank Transfer' },
                    { label: 'Online', value: 'Online' },
                  ]}
                  defaultValue={{ label: formData.payment_method, value: formData.payment_method }}
                />
              </div>
              <div className="col-12 col-md-4 mb-3 custom-select">
                <Label label={t('payment_frequency')} isRequired />
                <Select
                  onChange={(value) => onFormChange('payment_frequency', value)}
                  className="form-control error-payment_frequency"
                  option={{ label: 'label', value: 'value' }}
                  isSearchable={true}
                  options={[
                    { label: 'Monthly', value: 'Monthly' },
                    { label: 'Quarterly', value: 'Quarterly' },
                    { label: 'Yearly', value: 'Yearly' },
                  ]}
                  defaultValue={{ label: formData.payment_frequency, value: formData.payment_frequency }}
                />
              </div>
              <div className="col-12 col-md-4 mb-3">
                <Input
                  isRequired
                  label={t('account_holder_name')}
                  value={formData.account_holder_name}
                  onChange={(e) => onFormChange('account_holder_name', e.target.value)}
                  className="form-control error-account_holder_name"
                  name="account_holder_name"
                />
              </div>
              <div className="col-12 col-md-4 mb-3">
                <Input
                  isRequired
                  label={t('bank_name')}
                  value={formData.bank_name}
                  onChange={(e) => onFormChange('bank_name', e.target.value)}
                  className="form-control error-bank_name"
                  name="bank_name"
                />
              </div>
              <div className="col-12 col-md-4 mb-3">
                <Input isRequired label={t('bank_branch')} value={formData.branch} onChange={(e) => onFormChange('branch', e.target.value)} className="form-control error-branch" name="branch" />
              </div>
              <div className="col-12 col-md-4 mb-3">
                <Input
                  isRequired
                  label={t('account_number')}
                  value={formData.bank_number}
                  onChange={(e) => onFormChange('bank_number', e.target.value)}
                  className="form-control error-bank_number"
                  name="bank_number"
                />
              </div>
              <div className="col-12 col-md-4 mb-3">
                <Input
                  label={t('iban_swift_code_for_international_if_needed')}
                  value={formData.iban_swift_code}
                  onChange={(e) => onFormChange('iban_swift_code', e.target.value)}
                  className="form-control error-iban_swift_code"
                  name="iban_swift_code"
                />
              </div>
              <div className="col-12 col-md-4 mb-3">
                <Input
                  isRequired
                  label={t('estimated_amount')}
                  type="number"
                  value={formData.estimated_amount}
                  onChange={(e) => onFormChange('estimated_amount', e.target.value)}
                  className="form-control error-estimated_amount"
                  name="estimated_amount"
                />
              </div>
            </div>
          )}
        </form>
      </div>
      <div className="d-flex justify-content-start gap-2 mt-3">
        <Button color="light" className="d-flex align-items-center gap-1" onClick={() => setToggleTab('coverage_info')}>
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

export default PaymentInfo;
