'use client';
import { useEffect, useState } from 'react';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams, useRouter } from 'next/navigation';
import { ISample } from '../../model';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { getOneClaim } from '../../api-service';

export const OtherPartyInfo = ({ toggleTableTab }: { toggleTableTab: Function }) => {
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
    toggleTableTab('witness_info');
  };

  return (
    <>
      <div className="mb-4">
        <div className="panel-title mb-3">{t('other_parties_involved')}</div>
        <div className="row">
          <div className="col-12 mb-3">
            <Description label={t('was_another_vehicle_involved')} value={data?.name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 mb-3">
            <Description label={t('driver_name')} value={data?.description || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('vehicle_type')} value={data?.description || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('vehicle_make')} value={data?.description || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('vehicle_model')} value={data?.description || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('license_plate_number')} value={data?.description || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('year_of_manufacture')} value={data?.description || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('registered_year')} value={data?.description || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('vehicle_identification_number')} value={data?.description || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('used_for')} value={data?.description || '-'} skeleton={skeleton} />
          </div>
        </div>
      </div>
      <div className="d-flex justify-content-start gap-2 mt-3">
        <Button
          color="light"
          className="d-flex align-items-center gap-1"
          onClick={() => {
            router.push(`/policy/a/claim/${claimId}?t=damage_info`);
          }}
        >
          <Flexicon icon="chevron-left" variant="line" size={18} />
          <span className="d-none d-sm-inline">{t('back')}</span>
        </Button>
        <Button color="primary" className="d-flex align-items-center gap-1" onClick={handleNextPage}>
          <span className="d-none d-sm-inline">{t('next')}</span>
          <Flexicon icon="chevron-right" variant="line" size={18} />
        </Button>
        <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => router.push(`/policy/a/claim/edit/?claimId=${claimId}&t=other_party_info`)}>
          <Flexicon icon="edit-05" variant="line" size={18} />
          <span className="d-none d-sm-inline">{t('edit')}</span>
        </Button>
        {/* <Button text={t('update')} type="submit" width="sm" isLoading={undefined} disabled={skeleton} />
                  <Button text={t('cancel')} color="light" width="sm" /> */}
      </div>
    </>
  );
};
