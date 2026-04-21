import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button, Skeleton } from '@apptimus-ui/ui-element';
import React, { useCallback, useEffect, useState } from 'react';
import RiskTypeList from './RiskTypeList';
import AddInfo from './AddInfo';
import { IElement } from '@/components/others/common/form/template-modal';
import { getAllOpportunityTypeFormAttributes } from '@/components/others/common/lead/api-service';
import { getAllOpportunityTypeFormElements } from '@/components/others/common/risk-type-view/api-service';
import EditRiskInfo from './EditRiskInfo';

const OpportunityTypes = ({
  selectedTypeId,
  customerId,
  leadId,
  selectedRiskIds,
  defaultRiskIds,
}: {
  selectedTypeId: string;
  customerId: any;
  leadId: any;
  selectedRiskIds: (ids: any) => void;
  defaultRiskIds: any[];
}) => {
  const t = useTrans('label.risks,otr.common');
  const [addInfoModal, setAddInfoModal] = useState(false);
  const [addInfoVers, setAddInfoVers] = useState(0);
  const [tableVers, setTableVers] = useState(0);
  const [loading, setLoading] = useState(true);
  const [tableElements, setTableElements] = useState<IElement[]>([]);
  const [editInfoId, setEditInfoId] = useState('');
  // const router = useRouter();
  console.log('defaultRiskIds', defaultRiskIds);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const responseData = await getAllOpportunityTypeFormAttributes(selectedTypeId, 'ONBOARDING');
        if (responseData?.is_success) {
          const response = await getAllOpportunityTypeFormElements(responseData.result.form_id || '');
          setTableElements(response?.result || []);
          setLoading(false);
        }
      } catch (error) {
        console.error('Error fetching form attributes:', error);
      }
    };

    if (selectedTypeId) {
      fetchData();
    }
  }, [selectedTypeId]);

  const reloadTable = () => {
    setTableVers((prev) => prev + 1);
  };

  const handleSelectedRiskIds = useCallback(
    (ids: any[], isTriggered: boolean) => {
      console.log('isTriggered', isTriggered);
      isTriggered ? selectedRiskIds(ids) : selectedRiskIds(defaultRiskIds);
    },
    [selectedRiskIds, defaultRiskIds],
  );

  return (
    <>
      {loading ? (
        <Skeleton height="300px" width="100%" />
      ) : (
        <>
          <div className="d-flex algin-items-center justify-content-end mb-3 px-2">
            {selectedTypeId && (
              <>
                {/* <Button color="light" className="d-flex align-items-center gap-1 me-2" onClick={() => router.push(`/policy/a/policy-request/upload-risk-info?leadId=${leadId}`)}>
                  <Flexicon icon="upload-01" size={18} />
                  <span className="d-none d-sm-inline">{t('upload_risk_info')}</span>
                </Button> */}
                <Button color="primary" className="d-flex align-items-center gap-1 me-2" onClick={() => setAddInfoModal(true)}>
                  <Flexicon icon="plus-circle" size={18} />
                  <span className="d-none d-sm-inline">{t('add_new_entity', { entity: t('info') })}</span>
                </Button>
              </>
            )}
          </div>

          {addInfoModal && (
            <AddInfo
              key={addInfoVers}
              isOpen={addInfoModal}
              onCancel={() => (setAddInfoModal(false), setAddInfoVers((prev) => prev + 1))}
              afterSave={() => (setTableVers((prev) => prev + 1), setAddInfoModal(false), setAddInfoVers((prev) => prev + 1), reloadTable())}
              opportunityId={leadId}
              typeId={selectedTypeId}
              customerId={customerId}
            />
          )}
          {tableElements.length > 0 && (
            <RiskTypeList
              riskTypeId={selectedTypeId}
              customerId={customerId}
              tableElements={tableElements}
              tableVers={tableVers}
              leadId={leadId}
              selectedRiskIds={handleSelectedRiskIds}
              defaultSelectedRiskIds={defaultRiskIds.map((risk) => ({ risk_id: risk }))}
              onEdit={(id: any) => setEditInfoId(id)}
            />
          )}
          {editInfoId !== '' && (
            <EditRiskInfo
              isOpen={!!editInfoId}
              onCancel={() => setEditInfoId('')}
              afterSave={() => {
                setEditInfoId('');
                reloadTable();
              }}
              riskInfoId={editInfoId}
            />
          )}
        </>
      )}
    </>
  );
};

export default OpportunityTypes;
