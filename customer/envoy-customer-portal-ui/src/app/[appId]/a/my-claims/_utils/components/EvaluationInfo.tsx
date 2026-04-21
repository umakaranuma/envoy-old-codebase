import { useParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import { IClaimEvaluationInfo } from '../model';
import { getOneClaimEvaluationInfo } from '../api-service';
import { Description } from '@/components/others/Description';
import { Skeleton } from '@apptimus-ui/ui-element';

function EvaluationInfo() {
  const params = useParams();
  const claimId = params.claimId as string;
  const [skeleton, setSkeleton] = useState(true);
  const [data, setData] = useState({} as IClaimEvaluationInfo);

  useEffect(() => {
    const fetchData = async () => {
      setSkeleton(true);
      const responseData = await getOneClaimEvaluationInfo(claimId);
      if (responseData?.is_success) {
        setData(responseData.result);
        setSkeleton(false);
      }
    };
    fetchData();
  }, []);
  return (
    <>
      {skeleton ? (
        <Skeleton width="100%" height="200px" />
      ) : (
        <div>
          {data.claim_status === 'Draft' ? (
            <div className="text-center fw-medium">No Records Found!</div>
          ) : (
            <>
              {data?.panels?.length > 0 &&
                data.panels.map((panel) => (
                  <div className="bg-white custom-card overflow-hidden p-3 rounded-3 mb-3" key={panel.id}>
                    <div className="fs-13 fw-semibold mb-3">{panel.title ? panel.title : ''}</div>
                    <div className="row">
                      {data.elements.length > 0 &&
                        data.elements
                          .filter((element) => element.panel_id === panel.id)
                          .map((element) => (
                            <div className="col-12 col-md-3 mb-3" key={element.id}>
                              <Description label={element.label} value={element.value || '-'} skeleton={skeleton} />
                            </div>
                          ))}
                    </div>
                  </div>
                ))}
            </>
          )}
        </div>
      )}
    </>
  );
}

export default EvaluationInfo;
