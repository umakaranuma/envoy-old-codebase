import React from 'react';
import { ContactView } from '../_utils/components/contact/ContactView';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Contacts',
};

function Page() {
  return <ContactView />;
}

export default Page;
