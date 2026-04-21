import React from 'react';
import { Metadata } from 'next';
import SalesTarget from './_utils/components/SalesTarget';

export const metadata: Metadata = {
  title: 'Sales Target',
};

async function SamplePg() {
  return <SalesTarget />;
}

export default SamplePg;
