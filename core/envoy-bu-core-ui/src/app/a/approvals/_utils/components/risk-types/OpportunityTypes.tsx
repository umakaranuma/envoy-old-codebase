import { Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import RiskTypeList from './RiskTypeList';
import { IElement } from '@/app/a/templates/_utils/model';
import { getAllOpportunityTypeConfig, getAllOpportunityTypeFormAttributes } from '../../api-service';

const OpportunityTypes = ({ approvalId, riskTypeIds, customerId }: { approvalId: string; riskTypeIds: any; customerId: string }) => {
  const [loading, setLoading] = useState(true);
  const [tableElements, setTableElements] = useState<IElement[]>([]);

  // useEffect(() => {
  //   const fetchData = async () => {
  //     try {
  //       const responseData = await getOpportunityInfoElements({}, approvalId);
  //       if (responseData?.is_success) {
  //         setTableElements(responseData.result.risks[0].elements || []);
  //         setLoading(false);
  //       }
  //     } catch (error) {
  //       console.error('Error fetching form attributes:', error);
  //     }
  //   };

  //   if (approvalId && riskTypeIds) {
  //     fetchData();
  //   }
  // }, [riskTypeIds]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const responseData = await getAllOpportunityTypeConfig(riskTypeIds, 'ONBOARDING');
        if (responseData?.is_success) {
          const response = await getAllOpportunityTypeFormAttributes(responseData.result.form_id || '');
          setTableElements(response?.result || []);
          setLoading(false);
        }
      } catch (error) {
        console.error('Error fetching form attributes:', error);
      }
    };

    if (riskTypeIds) {
      fetchData();
    }
  }, [riskTypeIds]);

  return (
    <>
      {loading ? (
        <Skeleton height="300px" width="100%" />
      ) : (
        <>{tableElements && <RiskTypeList riskTypeId={riskTypeIds} customerId={customerId} tableElements={tableElements || []} approvalId={approvalId} />}</>
      )}
    </>
  );
};

export default OpportunityTypes;
