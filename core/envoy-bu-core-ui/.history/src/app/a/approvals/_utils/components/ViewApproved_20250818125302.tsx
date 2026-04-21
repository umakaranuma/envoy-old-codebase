import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Badge, Button } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { getOneApproval } from '../api-service';
import { IApproval } from '../model';
import { formatDate } from '@/helpers/services/commonService';
import OpportunityTypes from './risk-types/OpportunityTypes';

function ViewApproved({ isOpen, onCancel, viewId, status }: { isOpen: boolean; onCancel: Function; viewId: string; status: string }) {
  const t = useTrans('label.approvals,otr.common');
  const [data, setData] = useState({} as IApproval);
  const [skeleton, setSkeleton] = useState(true);
  const [activeSelectedTab, setSelectedActiveTab] = useState(0);

  useEffect(() => {
    if (viewId) {
      setSkeleton(true);
      fetchData();
    }
  }, [viewId]);

  const fetchData = async () => {
    const responseData = await getOneApproval(viewId);
    if (responseData?.is_success) {
      setData(responseData.result);
      setSkeleton(false);
      // if (responseData.result?.service_providers?.length) {
      //     setSelectedServiceProviders(
      //         responseData.result.service_providers.map((provider: IServiceProvider) => ({
      //             id: provider.service_provider_id,
      //             name: provider.service_provider_name,
      //             checked: true,
      //         })),
      //     );
      // }
    }
  };

  return (
    <Modal isOpen={isOpen} size="lg" scrollable>
      <ModalHeader title={t('view_approval')} onClose={() => onCancel()} />
      <ModalBody>
        <div className="bg-light p-3 rounded-1 mb-3">
          <div className="row">
            <div className="panel-title">{t('request_details')}</div>
            <div className="col-6 col-md-6 col-lg-4 mb-3">
              <Description label={t('quotation_request_id')} value={data?.code || '-'} skeleton={skeleton} />
            </div>
            <div className="col-6 col-md-6 col-lg-4 mb-3">
              <Description label={t('category')} value={<Badge text={data?.entity_type} color={data?.entity_type === 'policy' ? 'primary' : 'warning'} radius="pill" />} skeleton={skeleton} />
            </div>
            <div className="col-6 col-md-6 col-lg-4 mb-3">
              <Description label={t('request_type')} value={data?.request_type || '-'} skeleton={skeleton} />
            </div>
            <div className="col-6 col-md-6 col-lg-4 mb-3">
              <Description label={t('request_date')} value={formatDate(data?.request_date) || '-'} skeleton={skeleton} />
            </div>
            <div className="col-6 col-md-6 col-lg-4 mb-3">
              <Description label={t('requested_by')} value={data?.created_by_name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-6 col-md-6 col-lg-4 mb-3">
              <Description label={t('customer_info')} value={data?.customer_name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-6 col-md-6 col-lg-4 mb-3">
              <Description label={status === 'approved' ? t('approved_by') : t('rejected_by')} value={data?.approved_by_name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-6 col-md-6 col-lg-4 mb-3">
              <Description label={t('date')} value={formatDate(data?.approval_date)} skeleton={skeleton} />
            </div>
            <div className="col-12 mb-3">
              <Description label={t('remarks')} value={data?.approval_remarks || '-'} skeleton={skeleton} />
            </div>
          </div>
        </div>
        {data.opportunity_types?.length > 0 && (
          <div className="bg-light p-3 rounded-1">
            <div className="panel-title">{t('risk_details')}</div>
            <div className="il-box-tab">
              {data.opportunity_types.map((riskType: any, index) => (
                <div key={riskType.id} className={`il-box-tab-item ${activeSelectedTab === index ? 'active' : ''}`} onClick={() => setSelectedActiveTab(index)}>
                  {riskType.title}
                </div>
              ))}
            </div>
            {data.opportunity_types.map((riskType: any, index) => (activeSelectedTab === index ? <OpportunityTypes approvalId={viewId} riskTypeIds={riskType.id} key={riskType.id} /> : null))}
          </div>
        )}
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('close')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default ViewApproved;
