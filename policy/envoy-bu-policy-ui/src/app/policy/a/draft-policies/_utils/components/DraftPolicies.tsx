'use client';
import React from 'react';
import DraftList from './DraftList';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';

function DraftPolicies() {
  const t = useTrans('label.draft_policies,otr.common,be.msg');
  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('draft_policies')} icon="core" />
      </div>
      <DraftList />
    </>
  );
}

export default DraftPolicies;
