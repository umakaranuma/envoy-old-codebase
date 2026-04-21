import React from 'react';
import { Metadata } from 'next';
import Sample from './_utils/components/Sample';

export const metadata: Metadata = {
  title: 'Sample CRUD',
};

async function SamplePg() {
  return <Sample />;
}

export default SamplePg;
