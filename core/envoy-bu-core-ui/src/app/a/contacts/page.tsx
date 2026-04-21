import React from 'react';
import Contacts from './_utils/components/Contacts';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Contacts',
};

function Page() {
  return <Contacts />;
}

export default Page;
