import React from 'react';
import { Metadata } from 'next';
import { InvoiceDetailsView } from '../_utils/components/InvoiceView';

export const metadata: Metadata = {
  title: 'Dr/Cr Note Details',
};

function page() {
  return <InvoiceDetailsView />;
}

export default page;
