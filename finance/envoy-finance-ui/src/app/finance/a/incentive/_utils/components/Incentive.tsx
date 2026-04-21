'use client';

import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import React, { useState } from 'react';
import IncentiveList from './IncentiveList';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { toaster } from '@/helpers/services/toaster';
import { runAllIncentive } from '../api-service';

function Incentive() {
  const t = useTrans('label.incentive,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [tableVers, setTableVers] = useState(0);
  const [isFormProcessing, setIsFormProcessing] = useState(false);

  async function onSubmit() {
    setIsFormProcessing(true);

    try {
      const responseData = await runAllIncentive();
      setIsFormProcessing(false);
      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setTableVers((prev) => prev + 1);
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }
  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('incentive')} icon="core" />
        <Button className="d-flex align-items-center gap-1" onClick={onSubmit} isLoading={isFormProcessing}>
          <Flexicon icon="tool-02" variant="line" size={18} />
          <span className="d-none d-sm-inline">{t('run')}</span>
        </Button>
      </div>
      <IncentiveList tableVers={tableVers} onView={() => {}} />
    </>
  );
}

export default Incentive;
