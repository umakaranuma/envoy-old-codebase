'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import React, { FormEvent, useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import IncentiveSetupCard from '../../create/components/IncentiveSetupCard';
import { emptyIncentive, IPerformanceField, LogicGroupNode } from '../../_utils/model';
import { Button, Input, Label, Skeleton } from '@apptimus-ui/ui-element';
import { getIncentiveSetupById, updateIncentiveSetup, getAllPerformanceField } from '../../_utils/api-service';
import { Flexicon } from '@apptimus-ui/flexicon';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import GoBack from '@/components/others/page-related/GoBack';
import { snakeToTitleCase, thousandSeparator } from '@/helpers/services/commonService';
import { getCurrency } from '@/helpers/services/currencyService';

export default function EditIncentiveSetupPage() {
  const t = useTrans('label.incentive_setup,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const router = useRouter();
  const params = useParams();
  const currency = getCurrency();
  const [formData, setFormData] = useState(emptyIncentive);
  const [performanceFieldData, setPerformanceFieldData] = useState<IPerformanceField[]>([]);
  const [skeleton, setSkeleton] = useState(true);
  const [isFormProcessing, setIsFormProcessing] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      setSkeleton(true);
      try {
        const [incentiveRes, perfFieldsRes] = await Promise.all([getIncentiveSetupById(params.id as string), getAllPerformanceField()]);
        if (incentiveRes?.is_success) {
          let perfFields = incentiveRes.result.performance_fields;
          if (typeof perfFields === 'string') {
            try {
              perfFields = JSON.parse(perfFields);
            } catch {
              perfFields = { logic: 'AND', conditions: [] };
            }
          }
          setFormData({ ...incentiveRes.result, performance_fields: perfFields });
        }
        if (perfFieldsRes?.is_success) {
          setPerformanceFieldData(perfFieldsRes.result);
        }
      } catch (error) {
        console.error(error);
      } finally {
        setSkeleton(false);
      }
    };
    if (params.id) fetchData();
  }, [params.id]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.incentive_setup.update);
    setIsFormProcessing(true);
    try {
      const responseData = await updateIncentiveSetup(params.id as string, formData);
      setIsFormProcessing(false);
      if (responseData.status_code === 417) {
        printError(responseData.result, form.incentive_setup.update, tBe);
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
      <GoBack goTo={() => router.push('/finance/a/incentive-setup')} title={t('edit_incentive_setup')} />
      <form onSubmit={onSubmit} id={`${form.incentive_setup.update}`}>
        <div className="panel">
          <div className="panel-title">{t('basic_details')}</div>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Label htmlFor="name" label={t('name')} />
              {skeleton ? <InputSkeleton /> : <Input value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" disabled />}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label htmlFor="description" label={t('description')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  type={'textarea'}
                  value={formData.description}
                  onChange={(e) => onFormChange('description', e.target.value)}
                  className="form-control error-description"
                  name="description"
                  disabled
                />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label htmlFor="start_date" label={t('start_date')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input type="date" value={formData.start_date} onChange={(e) => onFormChange('start_date', e.target.value)} className="form-control error-start_date" name="start_date" disabled />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label htmlFor="end_date" label={t('end_date')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input type="date" value={formData.end_date} onChange={(e) => onFormChange('end_date', e.target.value)} className="form-control error-end_date" name="end_date" disabled />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('reward_type')} />
              {skeleton ? <InputSkeleton /> : <Input value={formData.reward_type_name} disabled />}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label htmlFor="reward_type_value" label={t('reward_type_value')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  type={'text'}
                  value={`${currency.code} ${thousandSeparator(formData.reward_type_value)}`}
                  onChange={(e) => onFormChange('reward_type_value', e.target.value)}
                  className="form-control error-reward_type_value"
                  name="reward_type_value"
                  disabled
                />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('repeation_type')} />
              {skeleton ? <InputSkeleton /> : <Input value={formData.repeation_type} disabled />}
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('incentive_base_field')} />
              {skeleton ? <InputSkeleton /> : <Input value={snakeToTitleCase(formData.incentive_base_field)} disabled />}
            </div>
          </div>
        </div>
        <div>
          {skeleton ? (
            <Skeleton height="400px" width="100%" className="mt-3" />
          ) : (
            <IncentiveSetupCard
              skeleton={skeleton}
              performanceFieldData={performanceFieldData}
              onUpdate={(newData) => {
                onFormChange('performance_fields', newData);
              }}
              defultLogicTree={formData.performance_fields as LogicGroupNode}
            />
          )}
        </div>
        <div className="d-flex justify-content-end gap-2  mt-4">
          <Button className="d-flex align-items-center gap-1" type="submit" isLoading={isFormProcessing}>
            <Flexicon icon="save-01" variant="line" size={18} />
            <span>{t('update')}</span>
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
