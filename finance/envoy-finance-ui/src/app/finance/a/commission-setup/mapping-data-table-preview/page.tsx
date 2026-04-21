import React from 'react';
import { Metadata } from 'next';
import MappingDataTablePreview from './_utils/components/MappingDataTablePreview';

export const metadata: Metadata = {
  title: 'MappingDataTablePreview',
};

function page() {
  return <MappingDataTablePreview />;
}

export default page;
