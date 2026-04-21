import React from 'react';
import { Metadata } from 'next';
import ServiceTypes from './_utils/components/ServiceTypes';

export const metadata: Metadata = {
  title: 'ServiceType',
};

function Page() {
  return <ServiceTypes />;
}

export default Page;
