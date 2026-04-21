import React from 'react';
import { Metadata } from 'next';
import { ServiceRenderedDetailsView } from '../_utils/components/ServiceRenderedView';

export const metadata: Metadata = {
  title: 'Service Rendered Details',
};

function page() {
  return <ServiceRenderedDetailsView />;
}

export default page;
