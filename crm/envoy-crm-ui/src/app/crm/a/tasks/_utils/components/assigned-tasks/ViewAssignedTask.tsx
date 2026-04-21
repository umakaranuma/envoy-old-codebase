'use client';
import { useEffect, useState } from 'react';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import Interaction from '../interaction/Interaction';
import StatusChangeList from '../StatusChangeList';
import ReassignmentList from '../ReassignmentList';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { IAssignedTask } from '../../model';
import { getOneAssignedTask } from '../../api-service';
import { formatDate, hexToRgba } from '@/helpers/services/commonService';
import GoBack from '@/components/others/page-related/GoBack';
import { Button } from '@apptimus-ui/ui-element';
import { useBreadcrumb } from '@/contexts/BreadcrumbContext';
import { Flexicon } from '@apptimus-ui/flexicon';
import { EditAssignedTask } from './EditAssignedTask';

export const ViewAssignedTask = () => {
  const t = useTrans('label.tasks,otr.common');
  const [data, setData] = useState({} as IAssignedTask);
  const [skeleton, setSkeleton] = useState(true);
  const [tab, setTab] = useState('interaction');
  const router = useRouter();
  const params = useParams();
  const viewId = params.taskId?.toString() || '';
  const searchParams = useSearchParams();
  const from = searchParams.get('f') || '';
  const { setCustomBreadcrumb } = useBreadcrumb();
  const [currentEditId, setCurrentEditId] = useState('');
  // const opId = searchParams.get('opId') || '';

  useEffect(() => {
    if (viewId) {
      setSkeleton(true);
      fetchData();
    }
  }, [viewId]);

  const fetchData = async () => {
    const responseData = await getOneAssignedTask(viewId);
    responseData?.is_success && (setData(responseData.result), setSkeleton(false));
  };

  useEffect(() => {
    setCustomBreadcrumb({
      text: t('view'),
      backurl: '/crm/a/tasks',
    });
    return () => setCustomBreadcrumb(null);
  }, [setCustomBreadcrumb]);

  const handleAfterUpdate = () => {
    setCurrentEditId('');
    fetchData();
  };

  return (
    <>
      <GoBack goTo={() => router.push(`${from === 'op' ? `/crm/a/tasks?t=assigned_tasks` : '/crm/a/tasks'}`)} title={t('task_management')} skeleton={skeleton} />
      <div className="panel">
        <div className="row my-2">
          <div className="col-12 col-md-4 mb-3">
            <Description
              label={t('lead_code')}
              value={
                <div className="clickable-text-primary" onClick={() => router.push(`/crm/a/sales-management/${data.opportunity_id}?t=tasks`)}>
                  {data.opportunity_code}
                </div>
              }
              skeleton={skeleton}
            />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('lead_name')} value={data?.opportunity_title || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description
              label={t('lead_stage')}
              value={
                <div
                  className={'rounded-5 fw-semibold badge error-lead_id'}
                  style={{ background: hexToRgba(data.opportunity_stage_color, 0.1), border: `1px solid ${hexToRgba(data.opportunity_stage_color, 0.4)}`, color: data.opportunity_stage_color }}
                >
                  {data.opportunity_stage_name}
                </div>
              }
              skeleton={skeleton}
            />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('task')} value={data?.task || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('description')} value={data?.description || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('assigned_date')} value={formatDate(data?.assigned_date as string) || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('start_date')} value={formatDate(data?.start_date as string) || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('due_date')} value={formatDate(data?.due_date as string) || '-'} skeleton={skeleton} />
          </div>
          {/* <div className="col-12 col-md-4 mb-3">
          <Description label={t('assigned_to')} value={data?.assigned_to_id || '-'} skeleton={skeleton} />
        </div> */}
          <div className="col-12 col-md-4 mb-3">
            <Description
              label={t('current_status')}
              value={
                <div
                  className={`rounded-5 fw-semibold badge`}
                  style={{ background: hexToRgba(data.task_status_color || '', 0.1), border: `1px solid ${data.task_status_color}`, color: data.task_status_color }}
                >
                  {data.task_status_name}
                </div>
              }
              skeleton={skeleton}
              isHtml={false}
            />
          </div>
        </div>
        <div className="d-flex justify-content-end">
          <Button onClick={() => setCurrentEditId(viewId)}>
            <span className="d-flex gap-2">
              <Flexicon icon="pencil-line" variant="line" size={17} />
              <span>{t('edit')}</span>
            </span>
          </Button>
        </div>
      </div>
      <div className="panel">
        <div className="il-box-tab">
          <div className={`il-box-tab-item ${tab === 'interaction' ? 'active' : ''}`} onClick={() => setTab('interaction')}>
            {t('interaction')}
          </div>
          <div className={`il-box-tab-item ${tab === 'status_change' ? 'active' : ''}`} onClick={() => setTab('status_change')}>
            {t('status_change')}
          </div>
          <div className={`il-box-tab-item ${tab === 'reassignment' ? 'active' : ''}`} onClick={() => setTab('reassignment')}>
            {t('reassignment')}
          </div>
        </div>

        <div className="">
          {tab === 'interaction' && <Interaction opportunityId={data.opportunity_id?.toString() || ''} />}
          {tab === 'status_change' && <StatusChangeList />}
          {tab === 'reassignment' && <ReassignmentList />}
        </div>
        {currentEditId !== '' && <EditAssignedTask editId={currentEditId} isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterUpdate={handleAfterUpdate} />}
      </div>
    </>
  );
};
