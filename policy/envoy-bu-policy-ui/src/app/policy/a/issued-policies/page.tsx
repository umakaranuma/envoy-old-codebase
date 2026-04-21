import React from 'react';
import IssuedPolicies from './_utils/components/IssuedPolicies';
import { getSetting } from '@/api-services/common';

async function page() {
  const response = await getSetting('OPPORTUNITY_CUSTOMER_REQUIRED_STAGE', 'server');
  const id = response?.result?.value || '';
  return <IssuedPolicies settingId={id} />;
}

export default page;
