import React from 'react';
import Commission from './_utils/components/Commission';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Commission',
};

function page() {
  return <Commission />;
}

export default page;
