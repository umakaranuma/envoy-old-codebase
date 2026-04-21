import { Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import RiskTypeList from './RiskTypeList';
import { getAllOpportunityTypeConfig, getAllOpportunityTypeFormAttributes } from '@/app/crm/a/sales-management/_utils/api-service';
import { IElement } from '../../model';

const OpportunityTypes = ({ riskTypeId, customerId, leadId }: { riskTypeId: any; customerId: string; leadId: string }) => {
  const [loading, setLoading] = useState(true);
  const [tableElements, setTableElements] = useState<IElement[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const responseData = await getAllOpportunityTypeConfig(riskTypeId, 'ONBOARDING');
        if (responseData?.is_success) {
          const response = await getAllOpportunityTypeFormAttributes(responseData.result.form_id || '');
          setTableElements(response?.result || []);
          setLoading(false);
        }
      } catch (error) {
        console.error('Error fetching form attributes:', error);
      }
    };

    if (riskTypeId) {
      fetchData();
    }
  }, [riskTypeId]);

  return (
    <>
      {loading ? (
        <Skeleton height="300px" width="100%" />
      ) : (
        <>{tableElements && <RiskTypeList riskTypeId={riskTypeId} customerId={customerId} tableElements={tableElements || []} leadId={leadId} />}</>
      )}
    </>
  );
};

export default OpportunityTypes;
