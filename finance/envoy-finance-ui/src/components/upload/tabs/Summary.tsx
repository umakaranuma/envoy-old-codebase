import React from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { Description } from '@/components/others/Description';
import { UploadSummaryData } from '@/interface/model';
import ErrorList from './ErrorList';

interface SummaryProps {
  data: UploadSummaryData;
}

function Summary({ data }: SummaryProps) {
  const t = useTrans('label.invoice,otr.common,be.msg');

  return (
    <div className="panel">
      <div className="fs-15 fw-semibold mb-3">{t('summary')}</div>
      <div className="mb-3">
        <div className="d-flex flex-row flex-wrap gap-3 justify-content-center py-3">
          <div className="d-flex flex-column align-items-center gap-2 bg-light p-2 px-4 rounded-3">
            <Description label={t('created')} value={data.result?.counts?.add_count?.toString() || '0'} />
          </div>
          <div className="d-flex flex-column align-items-center gap-2 bg-light p-2 px-4 rounded-3">
            <Description label={t('updated')} value={data.result?.counts?.update_count?.toString() || '0'} />
          </div>
          <div className="d-flex flex-column align-items-center gap-2 bg-light p-2 px-4 rounded-3">
            <Description label={t('ignored')} value={data.result?.counts?.ignore_count?.toString() || '0'} />
          </div>
          <div className="d-flex flex-column align-items-center gap-2 bg-light p-2 px-4 rounded-3">
            <Description label={t('errors')} value={data.result?.counts?.ignore_count?.toString()} />
          </div>
          <div className="d-flex flex-column align-items-center gap-2 bg-light p-2 px-4 rounded-3">
            <Description label={t('total')} value={data.result?.counts?.total_count?.toString() || '0'} />
          </div>
        </div>
      </div>
      {data.result?.results && data.result.results.length > 0 && (
        <div className="mt-4">
          <h6 className="mb-3">{t('detailed_changes')}</h6>
          <ErrorList data={data} />
        </div>
      )}
    </div>
  );
}

export default Summary;
