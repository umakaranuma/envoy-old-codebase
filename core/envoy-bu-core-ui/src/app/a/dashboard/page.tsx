import React from 'react';
import { Metadata } from 'next';
import { useServerTrans } from '@/helpers/services/lang/langServerService';
import PageHeading from '@/components/others/PageHeading';

export const metadata: Metadata = {
  title: 'Dashboard',
};

async function DashboardPg() {
  const t = await useServerTrans('label.dashboard');

  return (
    <div className="page-header-breadcrumb custom-page-header">
      <PageHeading title={t('dashboard')} icon="dashboard" />
    </div>
  );
}

export default DashboardPg;
