import React from 'react';
import Nodes from './_utils/components/Nodes';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Org Nodes',
};

function page() {
  return <Nodes />;
}

export default page;
