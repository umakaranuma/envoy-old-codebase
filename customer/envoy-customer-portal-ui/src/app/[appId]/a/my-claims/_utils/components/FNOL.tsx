import { useParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import { IClaimEvaluationInfo } from '../model';
import { getOneClaimFNOLInfo } from '../api-service';
import { Description } from '@/components/others/Description';
import { Skeleton } from '@apptimus-ui/ui-element';

function FNOL() {
  // const t = useTrans('otr.common');
  const params = useParams();
  const claimId = params.claimId as string;
  const [skeleton, setSkeleton] = useState(true);
  const [data, setData] = useState({} as IClaimEvaluationInfo);
  // const router = useRouter();
  // const appId = params.appId as string;

  useEffect(() => {
    const fetchData = async () => {
      setSkeleton(true);
      const responseData = await getOneClaimFNOLInfo(claimId);
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
          {/* <div className="d-flex justify-content-end gap-2 my-3 px-3">
            <Button className="d-flex align-items-center gap-1" isLoading={skeleton} onClick={() => router.push(`/${appId}/a/my-claims/${claimId}/edit`)}>
              <Flexicon icon="edit-05" variant="line" size={18} />
              <span>{t('edit')}</span>
            </Button>
          </div> */}

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
        </div>
      )}
    </>
  );
}

export default FNOL;
