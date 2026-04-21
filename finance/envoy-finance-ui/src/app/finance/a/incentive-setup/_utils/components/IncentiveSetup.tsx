'use client';

import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button } from '@apptimus-ui/ui-element';
import { useRouter } from 'next/navigation';
import React, { useState } from 'react';
import IncentiveSetupList from './IncentiveSetupList';
import { deleteIncentiveSetup } from '../api-service';
import { toaster } from '@/helpers/services/toaster';

function IncentiveSetup() {
  const t = useTrans('label.incentive_setup,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const router = useRouter();
  const [tableVers, setTableVers] = useState(0);

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteIncentiveSetup(deleteId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      onClose();
      setTableVers((prevTableVers) => prevTableVers + 1);
    }
  };

  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('incentive_setup')} icon="core" />
        <Button className="d-flex align-items-center gap-1" onClick={() => router.push('/finance/a/incentive-setup/create')}>
          <Flexicon icon="plus-circle" size={18} />
          <span className="d-none d-sm-inline">{t('add_new')}</span>
        </Button>
      </div>
      <IncentiveSetupList
        tableVers={tableVers}
        onView={(id: string) => {
          router.push(`/finance/a/incentive-setup/${id}`);
        }}
        onEdit={(id: string) => router.push(`/finance/a/incentive-setup/${id}/edit`)}
        handleOnDelete={handleOnDelete}
      />
    </>
  );
}

export default IncentiveSetup;
