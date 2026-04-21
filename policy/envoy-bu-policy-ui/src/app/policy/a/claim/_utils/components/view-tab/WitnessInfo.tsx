'use client';
import { useEffect, useState } from 'react';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams, useRouter } from 'next/navigation';
import { ISample } from '../../model';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { getOneClaim } from '../../api-service';

export const WitnessInfo = ({ toggleTableTab }: { toggleTableTab: Function }) => {
  const t = useTrans('label.claim,otr.common');
  const [data, setData] = useState({} as ISample);
  const [skeleton, setSkeleton] = useState(true);
  const params = useParams();
  const claimId = params.claimId?.toString() || '';
  const router = useRouter();

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneClaim(claimId);
      responseData?.is_success && (setData(responseData.result), setSkeleton(false));
    };

    if (claimId) {
      setSkeleton(true);
      fetchData();
    }
  }, [claimId]);

  const handleNextPage = () => {
    toggleTableTab('clam_settlement_info');
  };

  return (
    <>
      <div className="mb-4">
        <div className="panel-title mb-3">{t('witness_information')}</div>
        <div className="row">
          <div className="col-12 mb-3">
            <Description label={t('was_there_a_witness')} value={data?.name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('witness_name')} value={data?.name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('contact_number')} value={data?.description || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 mb-3">
            <Description label={t('witness_statement')} value={data?.description || '-'} skeleton={skeleton} />
          </div>
        </div>
      </div>
      <div className="d-flex justify-content-start gap-2 mt-3">
        <Button
          color="light"
          className="d-flex align-items-center gap-1"
          onClick={() => {
            router.push(`/policy/a/claim/${claimId}?t=other_party_info`);
          }}
        >
          <Flexicon icon="chevron-left" variant="line" size={18} />
          <span className="d-none d-sm-inline">{t('back')}</span>
        </Button>
        <Button color="primary" className="d-flex align-items-center gap-1" onClick={handleNextPage}>
          <span className="d-none d-sm-inline">{t('next')}</span>
          <Flexicon icon="chevron-right" variant="line" size={18} />
        </Button>
        <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => router.push(`/policy/a/claim/edit/?claimId=${claimId}&t=witness_info`)}>
          <Flexicon icon="edit-05" variant="line" size={18} />
          <span className="d-none d-sm-inline">{t('edit')}</span>
        </Button>
        {/* <Button text={t('update')} type="submit" width="sm" isLoading={undefined} disabled={skeleton} />
                  <Button text={t('cancel')} color="light" width="sm" /> */}
      </div>
    </>
  );
};
