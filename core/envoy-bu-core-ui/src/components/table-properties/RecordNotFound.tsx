import { useTrans } from '@/helpers/services/lang/langService';
import React from 'react';

function RecordNotFound() {
  const t = useTrans('otr.common');
  return (
    <div className="text-center px-5 py-4">
      <div className="text-muted fw-semibold my-2 fs-table">{t('no_records_found')}</div>
      <div className="text-muted fs-table">{t('no_records_found_info')}</div>
    </div>
  );
}

export default RecordNotFound;
