import React from 'react';
import ViewReport from '../_utils/components/ViewReport';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'CustomReport',
};

function page() {
  return <ViewReport />;
}

export default page;
