import React from 'react';
import Form from './_utils/components/Form';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Forms',
};

function Page() {
  return <Form />;
}

export default Page;
