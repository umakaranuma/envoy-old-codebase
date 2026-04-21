'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import React, { FormEvent, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import IncentiveSetupCard from './components/IncentiveSetupCard';
import { initFormData, IPerformanceField } from '../_utils/model';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllIncentiveBaseFieldData, fetchAllRepeationTypeData } from '../_utils/services';
import { createIncentiveSetup, getAllPerformanceField } from '../_utils/api-service';
import { Flexicon } from '@apptimus-ui/flexicon';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import GoBack from '@/components/others/page-related/GoBack';

export default function Page() {
  const t = useTrans('label.incentive_setup,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const router = useRouter();
  const [formData, setFormData] = useState(initFormData);
  const [performanceFieldData, setPerformanceFieldData] = useState<IPerformanceField[]>([]);
  const [skeleton, setSkeleton] = useState(true);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      setSkeleton(true);
      try {
        const responseData = await getAllPerformanceField();
        if (responseData?.is_success) {
          const data: IPerformanceField[] = responseData.result;
          setPerformanceFieldData(data);
        }
      } catch (error) {
        console.error(error);
      } finally {
        setSkeleton(false);
      }
    };
    fetchData();
  }, []);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.incentive_setup.store);
    setIsFormProcessing(true);
    try {
      const responseData = await createIncentiveSetup(formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        if (responseData.result?.performance_fields) {
          setError(responseData.result.performance_fields);
        }
        printError(responseData.result, form.incentive_setup.store, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        router.push('/finance/a/incentive-setup');
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <div>
      <GoBack goTo={() => router.back()} title={t('incentive_setup')} />
      <form onSubmit={onSubmit} id={`${form.incentive_setup.store}`}>
        <div className="panel">
          <div className="panel-title">{t('basic_details')}</div>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Input isRequired label={t('name')} value={formData?.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                type={'textarea'}
                label={t('description')}
                value={formData?.description}
                onChange={(e) => onFormChange('description', e.target.value)}
                className="form-control error-description"
                name="description"
              />
            </div>
            <div className="col-12  my-3">
              <div className="row">
                <div className="col-12 col-md-6 mb-3">
                  <Label htmlFor="reward_type" label={t('reward_type')} isRequired />
                  <div className="mb-3 d-flex flex-row gap-2 align-items-center">
                    <input
                      type="radio"
                      id="fixed"
                      name="reward_type"
                      value="fixed"
                      className="mb-2"
                      onChange={(e) => {
                        onFormChange('reward_type', e.target.value), onFormChange('reward_type_id', 1);
                      }}
                      checked={formData?.reward_type === 'fixed'}
                    />
                    <Label htmlFor="fixed" label={t('fixed')} />
                    <input
                      type="radio"
                      id="percentage"
                      name="reward_type"
                      value="percentage"
                      className="mb-2"
                      onChange={(e) => {
                        onFormChange('reward_type', e.target.value), onFormChange('reward_type_id', 2);
                      }}
                      checked={formData?.reward_type === 'percentage'}
                    />
                    <Label htmlFor="percentage" label={t('percentage')} />
                  </div>
                </div>
                <div className="col-12 col-md-6 mb-3">
                  <Input
                    label={t('reward_type_value')}
                    value={formData?.reward_type_value}
                    onChange={(e) => onFormChange('reward_type_value', e.target.value)}
                    className="form-control error-reward_type_value"
                    name="reward_type_value"
                    type="number"
                    isRequired
                  />
                </div>
              </div>
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                type="date"
                label={t('start_date')}
                value={formData?.start_date}
                onChange={(e) => onFormChange('start_date', e.target.value)}
                className="form-control error-start_date"
                name="start_date"
                isRequired
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                type="date"
                label={t('end_date')}
                value={formData?.end_date}
                onChange={(e) => onFormChange('end_date', e.target.value)}
                className="form-control error-end_date"
                name="end_date"
                isRequired
              />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('repeation_type')} isRequired />
              <AsyncSelect
                onChange={(_, data) => {
                  onFormChange('repeation_type', data.name);
                }}
                className="form-control error-repeation_type"
                loadOptions={fetchAllRepeationTypeData}
                option={{
                  value: 'id',
                  label: 'name',
                }}
              />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('incentive_base_field')} isRequired />
              <AsyncSelect
                onChange={(value) => {
                  onFormChange('incentive_base_field', value);
                }}
                className="form-control error-incentive_base_field"
                loadOptions={fetchAllIncentiveBaseFieldData}
                option={{
                  value: 'value',
                  label: 'label',
                  labelFn: (option) => <div title={option.description || ''}>{option.label}</div>,
                }}
              />
            </div>
          </div>
        </div>
        <div>
          <IncentiveSetupCard
            error={error}
            skeleton={skeleton}
            performanceFieldData={performanceFieldData}
            onUpdate={(newData) => {
              onFormChange('performance_fields', newData);
            }}
          />
        </div>

        <div className="d-flex justify-content-end gap-2  mt-4">
          <Button className="d-flex align-items-center gap-1" type="submit" isLoading={isFormProcessing}>
            <Flexicon icon="save-01" variant="line" size={18} />
            <span>{t('create')}</span>
          </Button>
          <Button
            text={t('cancel')}
            color="light"
            width="sm"
            onClick={() => {
              router.back();
            }}
          />
        </div>
      </form>
    </div>
  );
}
