import { Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import RiskTypeList from './RiskTypeList';
import { IElement } from '@/components/others/common/form/template-modal';
import { getAllOpportunityTypeFormAttributes } from '@/components/others/common/lead/api-service';
import { getAllOpportunityTypeFormElements } from './api-service';

const ViewRiskTypes = ({ selectedTypeId, customerId, leadId, policyBaseId }: { selectedTypeId: string; customerId: any; leadId?: any; policyBaseId?: string }) => {
  const [loading, setLoading] = useState(true);
  const [tableElements, setTableElements] = useState<IElement[]>([]);
  console.log(leadId);

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

  return (
    <>
      {loading ? (
        <Skeleton height="300px" width="100%" />
      ) : (
        <>{tableElements.length > 0 && <RiskTypeList riskTypeId={selectedTypeId} customerId={customerId} policyBaseId={policyBaseId} tableElements={tableElements} />}</>
      )}
    </>
  );
};

export default ViewRiskTypes;
