import React from 'react';
import CustomReports from './_utils/components/CustomReports';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'CustomReport',
};

function Page() {
  return <CustomReports />;
}

export default Page;
