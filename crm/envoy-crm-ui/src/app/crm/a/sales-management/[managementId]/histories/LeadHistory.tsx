'use client';

import { hexToRgba } from '@/helpers/services/commonService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Input, Skeleton } from '@apptimus-ui/ui-element';
import { useParams, useRouter } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import { Activity, ActivityResult, IOpportunity } from '../../_utils/model';
import { getAllEntitiesActivities, getOneOpportunity } from '../../_utils/api-service';
import ContactCard from '../../../tasks/_utils/components/assigned-tasks/kanban-view/ContactCard';
import { useTrans } from '@/helpers/services/lang/langService';
import GoBack from '@/components/others/page-related/GoBack';

const LeadHistory: React.FC = () => {
  const router = useRouter();
  const [skeleton, setSkeleton] = useState(true);
  const [data, setData] = useState({} as IOpportunity);
  const [entityData, setEntityData] = useState({} as ActivityResult);
  const params = useParams();
  const opportunityId = params.managementId?.toString() || '';
  const [formData, setFormData] = useState('');
  const [toData, setToData] = useState('');
  const t = useTrans('label.sales_managements,otr.common,be.msg');
  const [entityDataskeleton, setentityDataSkeleton] = useState(true);
  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneOpportunity(opportunityId);
      if (responseData?.is_success) {
        setData(responseData.result);
        setSkeleton(false);
      }
    };

    if (opportunityId) {
      setSkeleton(true);
      fetchData();
    }
  }, [opportunityId]);

  useEffect(() => {
    const fetchData = async () => {
      if (!data.entity_id) return;

      const responseData = await getAllEntitiesActivities(data.entity_id.toString(), formData, toData, 'desc', '200');
      if (responseData?.is_success) {
        setEntityData(responseData.result);
        setentityDataSkeleton(false);
      }
    };

    fetchData();
  }, [data.entity_id, formData, toData]);

  function formatTimestamp(originalTimestamp: string) {
    const utcTimestamp = originalTimestamp.endsWith('Z') ? originalTimestamp : originalTimestamp + 'Z';

    const date = new Date(utcTimestamp);

    return date.toLocaleString('en-US', {
      timeZone: 'Asia/Colombo',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    });
  }

  return (
    <>
      <div className="d-flex align-items-center gap-3 py-2">
        <GoBack goTo={() => router.push('/crm/a/sales-managements')} title={data.title} skeleton={skeleton} />
        <div
          className={`rounded-5 fw-semibold badge ms-3`}
          style={{ background: hexToRgba(data?.stage_color ?? '', 0.1), border: `1px solid ${hexToRgba(data?.stage_color ?? '', 0.4)}`, color: data.stage_color }}
        >
          {data.stage_name}
        </div>
      </div>
      <div className="bg-white custom-card overflow-hidden p-2 px-4 pt-2 rounded-3">
        <div className="card-header d-flex justify-content-between align-items-center mb-3">
          <div className="card-title">{t('leads_history')}</div>
          <div className="d-flex gap-3 justify-content-center align-items-center">
            <div className="d-flex align-items-center gap-2">
              <span className="text-nowrap text-muted fw-medium fs-11">{t('from')} :</span>
              <Input type="date" value={formData} onChange={(e) => setFormData(e.target.value)} className="form-control error-description mb-0" id="from" name="from" />
            </div>
            <div className="d-flex align-items-center gap-2">
              <span className="text-nowrap text-nowrap text-muted fw-medium fs-11">{t('to')} :</span>
              <Input type="date" value={toData} onChange={(e) => setToData(e.target.value)} className="form-control error-description mb-0" id="to" name="to" />
            </div>
          </div>
        </div>
        <div className="card-body">
          <ul className="list-unstyled mb-0 crm-recent-activity">
            {entityDataskeleton ? (
              <div className="d-flex gap-3 aligin-items-center">
                <Skeleton height="30px" width="30px" className="rounded-circle" />
                <Skeleton height="30px" width="300px" />
              </div>
            ) : (
              <>
                {entityData.data?.map((item: Activity) => (
                  <li key={item.id} className="crm-recent-activity-content">
                    <div className="d-flex align-items-top">
                      <div className="me-3">
                        <span className={`avatar avatar-xs bg-primary-transparent avatar-rounded`}>
                          <Flexicon icon="check-circle" variant="solid" size={50} />
                        </span>
                      </div>
                      <div className="">
                        <div className="fw-semibold mb-1">{item.activity}</div>
                        <div className="d-block text-muted fs-11 op-7 mb-1">{formatTimestamp(item.added_at)}</div>
                        <ContactCard name={item.added_by_name} />
                      </div>
                    </div>
                  </li>
                ))}
              </>
            )}
          </ul>
        </div>
      </div>
    </>
  );
};

export default LeadHistory;
