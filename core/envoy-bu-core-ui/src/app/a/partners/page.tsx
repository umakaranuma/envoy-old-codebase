import React from 'react';
import Partners from './_utils/components/Partners';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Partners',
};

function Page() {
  return <Partners />;
}

export default Page;
