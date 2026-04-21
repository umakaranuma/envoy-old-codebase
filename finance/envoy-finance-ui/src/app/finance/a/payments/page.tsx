import React from 'react';
import Payments from './_utils/components/Payments';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Payments',
};

function page() {
  return <Payments />;
}

export default page;
