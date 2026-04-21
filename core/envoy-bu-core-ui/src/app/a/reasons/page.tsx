import React from 'react';
import Reason from './_utils/components/Reason';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Reasons',
};

function page() {
  return <Reason />;
}

export default page;
