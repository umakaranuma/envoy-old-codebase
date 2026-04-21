'use client';
import React from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import MyClaimsList from './MyClaimsList';
import { useParams, useRouter } from 'next/navigation';

function MyClaims() {
  const t = useTrans('label.my_claims,otr.common');
  const params = useParams();
  const appId = params.appId as string;
  const router = useRouter();
  return (
    <div className="bg-white rounded-2 pt-3 pb-1 px-3">
      <div className="fs-18 fw-semibold mb-3">{t('my_claims')}</div>
      {/* onEdit={(id: string) => router.push(`/${appId}/a/my-claims/${id}/edit`)} */}
      <MyClaimsList onView={(id: string) => router.push(`/${appId}/a/my-claims/${id}`)} />
    </div>
  );
}

export default MyClaims;
