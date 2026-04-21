import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button, Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { ICommissionSetting, initCommissionSettings } from './_utils/model';
import { getCommissionConfig, updateCommissionConfig } from './_utils/api-service';
import { toaster } from '@/helpers/services/toaster';

function CommissionConfig() {
  const t = useTrans('label.general_settings,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [commissionConfig, setCommissionConfig] = useState('');
  const [paymentFrequency, setPaymentFrequency] = useState('');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initCommissionSettings);
  const [skeleton, setSkeleton] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setSkeleton(true);
        const responseData = await getCommissionConfig();
        if (responseData?.is_success) {
          const jsonString = responseData.result.value.replace(/'/g, '"');
          const data = JSON.parse(jsonString) as ICommissionSetting;
          setPaymentFrequency(data.payment_frequency);
          setCommissionConfig(data.agent_commission_config);
          onFormChange('agent_commission_config', data.agent_commission_config);
          onFormChange('payment_frequency', data.payment_frequency);
          setSkeleton(false);
        }
      } catch (error) {
        console.log(error);
      }
    };
    fetchData();
  }, []);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  const handleCommissionChange = (e: any) => {
    setCommissionConfig(e.target.value);
    onFormChange('agent_commission_config', e.target.value);
  };

  const handleFrequencyChange = (e: any) => {
    setPaymentFrequency(e.target.value);
    onFormChange('payment_frequency', e.target.value);
  };

  async function onSubmit() {
    setIsFormProcessing(true);

    try {
      const transformedData = {
        value: {
          agent_commission_config: formData.agent_commission_config,
          payment_frequency: formData.payment_frequency,
        },
      };
      const responseData = await updateCommissionConfig(transformedData);
      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setFormData(initCommissionSettings);
      }
    } catch (error) {
      console.error('An error occurred:', error);
    } finally {
      setIsFormProcessing(false);
    }
  }

  return (
    <div>
      {/* 1. Agent Commission Config */}
      <div className="mb-4">
        <div className="fw-semibold mb-3">1. {t('agent_commission_config')}</div>
        <div className="ms-0 ms-md-3">
          {skeleton ? (
            <>
              {[1, 2, 3, 4].map((item) => (
                <div className="mb-3 d-flex align-items-center gap-2" key={item}>
                  <Skeleton height="20px" width="20px" className="rounded-pill" />
                  <Skeleton height="20px" width="250px" />
                </div>
              ))}
            </>
          ) : (
            <>
              <div className="form-check mb-3">
                <input
                  className="form-check-input"
                  type="radio"
                  name="commissionConfig"
                  id="totalPremium"
                  value="totalPremium"
                  checked={commissionConfig === 'totalPremium'}
                  onChange={handleCommissionChange}
                />
                <label className="form-check-label" htmlFor="totalPremium">
                  {t('calculate_based_on_the_total_premium')}
                </label>
              </div>
              <div className="form-check mb-3">
                <input
                  className="form-check-input"
                  type="radio"
                  name="commissionConfig"
                  id="receivedAmount"
                  value="receivedAmount"
                  checked={commissionConfig === 'receivedAmount'}
                  onChange={handleCommissionChange}
                />
                <label className="form-check-label" htmlFor="receivedAmount">
                  {t('calculate_based_on_the_received_amount')}
                </label>
              </div>
            </>
          )}
        </div>
      </div>
      {/* 2. Payment Frequency */}
      <div>
        <div className="fw-semibold mb-3">2. {t('payment_frequency')}</div>
        <div className="ms-0 ms-md-3">
          {skeleton ? (
            <>
              {[1, 2, 3, 4].map((item) => (
                <div className="mb-3" key={item}>
                  <div className="d-flex align-items-start gap-2 mb-1">
                    <Skeleton height="20px" width="20px" className="rounded-pill" />
                    <div>
                      <Skeleton height="20px" width="150px" className="mb-2" />
                      <Skeleton height="20px" width="300px" />
                    </div>
                  </div>
                </div>
              ))}
            </>
          ) : (
            <>
              <div className="form-check mb-3">
                <input className="form-check-input" type="radio" name="paymentFrequency" id="monthly" value="monthly" checked={paymentFrequency === 'monthly'} onChange={handleFrequencyChange} />
                <label className="form-check-label" htmlFor="monthly">
                  {t('monthly')}
                  <div className="text-muted small">({t('commission_is_paid_at_the_end_of_each_month')})</div>
                </label>
              </div>

              <div className="form-check mb-3">
                <input className="form-check-input" type="radio" name="paymentFrequency" id="quarterly" value="quarterly" checked={paymentFrequency === 'quarterly'} onChange={handleFrequencyChange} />
                <label className="form-check-label" htmlFor="quarterly">
                  {t('quarterly')}
                  <div className="text-muted small">({t('commission_is_paid_every_3_months')})</div>
                </label>
              </div>

              <div className="form-check mb-3">
                <input
                  className="form-check-input"
                  type="radio"
                  name="paymentFrequency"
                  id="biAnnually"
                  value="biAnnually"
                  checked={paymentFrequency === 'biAnnually'}
                  onChange={handleFrequencyChange}
                />
                <label className="form-check-label" htmlFor="biAnnually">
                  {t('bi_annually')}
                  <div className="text-muted small">({t('commission_is_paid_every_6_months')})</div>
                </label>
              </div>

              <div className="form-check ps-3">
                <input
                  className="form-check-input"
                  type="radio"
                  name="paymentFrequency"
                  id="onIssuance"
                  value="onIssuance"
                  checked={paymentFrequency === 'onIssuance'}
                  onChange={handleFrequencyChange}
                />
                <label className="form-check-label" htmlFor="onIssuance">
                  {t('on_policy_issuance')}
                  <div className="text-muted small">({t('commission_is_paid_immediately_upon_policy_issuance')})</div>
                </label>
              </div>
            </>
          )}
        </div>
      </div>

      <div className="d-flex justify-content-end gap-2 mt-3">
        <Button text={t('cancel')} color="light" width="sm" />
        <Button className="d-flex align-items-center gap-1" isLoading={isFormProcessing} onClick={() => onSubmit()}>
          <Flexicon icon="save-01" variant="line" size={18} />
          <span>{t('save_changes')}</span>
        </Button>
      </div>
    </div>
  );
}

export default CommissionConfig;
