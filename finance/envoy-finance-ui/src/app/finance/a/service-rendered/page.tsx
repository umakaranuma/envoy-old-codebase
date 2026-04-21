import React from 'react';
import ServiceRendered from './_utils/components/ServiceRendered';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Service Rendered',
};

function page() {
  return <ServiceRendered />;
}

export default page;
