import React from 'react';
import { Metadata } from 'next';
import GeneralLedger from './_utils/components/GeneralLedger';

export const metadata: Metadata = {
  title: 'GeneralLedger',
};

function Page() {
  return <GeneralLedger />;
}

export default Page;
