import React from 'react';
import { Metadata } from 'next';
import SalesManagements from './_utils/components/SalesManagements';
import { getSetting } from '@/api-services/common';

export const metadata: Metadata = {
  title: 'Sales Management',
};

async function OpportunityPage({ searchParams }: any) {
  const response = await getSetting('OPPORTUNITY_CUSTOMER_REQUIRED_STAGE', 'server');
  const id = response?.result?.value || '';

  const searchParamsResolved = await searchParams;
  const act = searchParamsResolved.act === 'list' ? 'list_view' : 'kanban_view';

  return <SalesManagements settingId={id.toString()} act={act} />;
}

export default OpportunityPage;
