import React from 'react';
import { Metadata } from 'next';
import GeneralSettings from './_utils/components/GeneralSettings';

export const metadata: Metadata = {
  title: 'General-Settings',
};

function Page() {
  return <GeneralSettings />;
}

export default Page;
