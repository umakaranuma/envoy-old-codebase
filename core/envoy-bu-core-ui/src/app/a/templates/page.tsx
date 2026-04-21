import React from 'react';
import { Metadata } from 'next';
import Templates from './_utils/components/Templates';

export const metadata: Metadata = {
  title: 'Templates',
};

function Page() {
  return <Templates />;
}

export default Page;
