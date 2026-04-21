'use client';
import GoBack from '@/components/others/page-related/GoBack';
import { useTrans } from '@/helpers/services/lang/langService';
import { useRouter } from 'next/navigation';
import React from 'react';
import CommissionCalculatedList from './CommissionCalculatedList';
import DeductibleList from './DeductibleList';

export default function CommissionSingleView() {
  const t = useTrans('label.commission,otr.common,be.msg');
  const router = useRouter();
  return (
    <div className="invoice-details-container">
      <GoBack goTo={() => router.push('/finance/a/commission?tab=commission_history')} title={t('commission_history')} />
      <div className="panel">
        <CommissionCalculatedList />
      </div>
      <div className="panel">
        <DeductibleList />
      </div>
    </div>
  );
}
