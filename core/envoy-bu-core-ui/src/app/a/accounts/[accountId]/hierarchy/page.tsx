import React from 'react';
import Hierarchy from '../../_utils/components/hierarchy/Hierarchy';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Account Hierarchy',
};

function Page() {
  return <Hierarchy />;
}

export default Page;
