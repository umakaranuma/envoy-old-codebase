'use client';

import { useTrans } from '@/helpers/services/lang/langService';
import React, { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { getIncentiveSetupById } from '../_utils/api-service';
import { getAllPerformanceField } from '../_utils/api-service';
import { IIncentive, IPerformanceField, LogicGroupNode } from '../_utils/model';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button, Skeleton } from '@apptimus-ui/ui-element';
import { Description } from '@/components/others/Description';
import IncentiveSetupCard from '../create/components/IncentiveSetupCard';
import GoBack from '@/components/others/page-related/GoBack';
import { getCurrency } from '@/helpers/services/currencyService';
import { snakeToTitleCase, thousandSeparator } from '@/helpers/services/commonService';

export default function IncentiveSetupViewPage() {
  const t = useTrans('label.incentive_setup,otr.common');
  const router = useRouter();
  const params = useParams();
  const currency = getCurrency();
  const [data, setData] = useState<IIncentive | null>(null);
  const [loading, setLoading] = useState(true);
  const [performanceFields, setPerformanceFields] = useState<IPerformanceField[]>([]);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const response = await getIncentiveSetupById(params.id as string);
        if (response?.is_success) {
          let perfFields = response.result.performance_fields;
          if (typeof perfFields === 'string') {
            try {
              perfFields = JSON.parse(perfFields);
            } catch {
              perfFields = { logic: 'AND', conditions: [] };
            }
          }
          setData({ ...response.result, performance_fields: perfFields });
        }
        const perfFieldsRes = await getAllPerformanceField();
        if (perfFieldsRes?.is_success) {
          setPerformanceFields(perfFieldsRes.result);
        }
      } catch (error) {
        // handle error
      } finally {
        setLoading(false);
      }
    }
    if (params.id) fetchData();
  }, [params.id]);

  return (
    <div>
      <GoBack goTo={() => router.back()} title={t('incentive_setup')} />
      <div className="panel">
        <div className="panel-title">{t('basic_details')}</div>
        <div className="row">
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('name')} value={data?.name} skeleton={loading} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('reward_type')} value={data?.reward_type || data?.reward_type} skeleton={loading} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description
              label={t('reward_type_value')}
              value={`${data?.reward_type === 'Fixed' ? currency.code + ' ' : ''}${thousandSeparator(data?.reward_type_value as string) || '-'}${data?.reward_type === 'Percentage' ? '%' : ''}`}
              skeleton={loading}
            />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('start_date')} value={data?.start_date} skeleton={loading} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('end_date')} value={data?.end_date} skeleton={loading} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('repeation_type')} value={data?.repeation_type} skeleton={loading} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('incentive_base_field')} value={snakeToTitleCase(data?.incentive_base_field as string)} skeleton={loading} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('description')} isTruncate={false} value={data?.description} skeleton={loading} />
          </div>
        </div>
      </div>
      <div>
        {loading ? (
          <Skeleton height="400px" width="100%" className="mt-3" />
        ) : (
          <IncentiveSetupCard skeleton={loading} performanceFieldData={performanceFields} onUpdate={() => {}} defultLogicTree={data?.performance_fields as LogicGroupNode} isView={true} />
        )}
      </div>
      <div className="d-flex justify-content-end gap-2  mt-4">
        <Button className="d-flex align-items-center gap-1" type="submit" onClick={() => router.push(`/finance/a/incentive-setup/${params.id}/edit`)}>
          <Flexicon icon="pencil-line" variant="line" size={18} className="me-1" />
          <span> {t('edit')}</span>
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
    </div>
  );
}
