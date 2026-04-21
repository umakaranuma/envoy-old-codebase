import React from 'react';
import { Metadata } from 'next';
import IncentiveSetup from './_utils/components/IncentiveSetup';

export const metadata: Metadata = {
  title: 'Incentive Setup',
};

function Page() {
  return <IncentiveSetup />;
}

export default Page;
