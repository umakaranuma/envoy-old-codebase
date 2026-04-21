import { Metadata } from 'next';
import React from 'react';
import MyQuotations from './_utils/components/MyQuotations';

export const metadata: Metadata = {
  title: 'My Quotations',
};

function Page() {
  return <MyQuotations />;
}

export default Page;
