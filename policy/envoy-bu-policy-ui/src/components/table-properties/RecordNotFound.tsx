import { useTrans } from '@/helpers/services/lang/langService';
import React from 'react';

function RecordNotFound() {
  const t = useTrans('otr.common');
  return (
    <div className="text-center px-5 py-4 fs-table">
      <div className="text-muted my-2">{t('no_records_found')}</div>
      <div className="text-muted">{t('no_records_found_info')}</div>
    </div>
  );
}

export default RecordNotFound;
