'use client';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import { IOpportunityType } from '../../../model';

export const BasicInfo = ({ data, skeleton }: { data: IOpportunityType; skeleton: boolean }) => {
  const t = useTrans('label.risks,otr.common');
  return (
    <div className="p-2 bg-white px-4 rounded-2 rounded-top-0">
      <div className="row">
        <div className="col-12 col-md-6 mb-3">
          <Description label={t('title')} value={data?.title || '-'} skeleton={skeleton} />
        </div>
        <div className="col-12 col-md-6 mb-3">
          <Description label={t('description')} value={data?.description || '-'} skeleton={skeleton} />
        </div>
      </div>
    </div>
  );
};
