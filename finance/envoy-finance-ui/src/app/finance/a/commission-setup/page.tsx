import React from 'react';
import { Metadata } from 'next';
import CommissionSetup from './_utils/components/CommissionSetup';

export const metadata: Metadata = {
  title: 'CommissionSetup',
};

function page() {
  return <CommissionSetup />;
}

export default page;
