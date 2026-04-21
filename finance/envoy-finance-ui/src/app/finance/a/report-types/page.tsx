import React from 'react';
import ReportTypes from './_utils/components/ReportTypes';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Report Type',
};

function Page() {
  return <ReportTypes />;
}

export default Page;
