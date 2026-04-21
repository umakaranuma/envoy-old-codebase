import React from 'react';
import Invoice from './_utils/components/Invoice';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Dr/Cr Note',
};

function page() {
  return <Invoice />;
}

export default page;
