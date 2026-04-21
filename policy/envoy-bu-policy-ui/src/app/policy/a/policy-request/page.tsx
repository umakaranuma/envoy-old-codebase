import React from 'react';
import { Metadata } from 'next';
import PolicyRequest from './_utils/components/PolicyRequest';
import { getSetting } from '@/api-services/common';

export const metadata: Metadata = {
  title: 'Policy Request',
};

async function PolicyRequestPg() {
  const response = await getSetting('OPPORTUNITY_CUSTOMER_REQUIRED_STAGE', 'server');
  const id = response?.result?.value || '';
  return <PolicyRequest settingId={id} />;
}

export default PolicyRequestPg;
