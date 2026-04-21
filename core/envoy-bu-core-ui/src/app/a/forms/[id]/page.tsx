import React from 'react';
import { ViewForm } from '../_utils/components/ViewForm';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Forms',
};

function Page() {
  return <ViewForm />;
}

export default Page;
