import React from 'react';
import { Metadata } from 'next';
import Incentive from './_utils/components/Incentive';

export const metadata: Metadata = {
  title: 'Incentive',
};

function Page() {
  return <Incentive />;
}

export default Page;
