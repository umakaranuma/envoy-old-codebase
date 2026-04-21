import React from 'react';
import Flags from './_utils/components/Flags';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Flags',
};

function page() {
  return <Flags />;
}

export default page;
