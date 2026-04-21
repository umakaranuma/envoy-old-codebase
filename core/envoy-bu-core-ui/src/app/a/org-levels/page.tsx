import React from 'react';
import { Metadata } from 'next';
import OrgLevels from './_utils/components/OrgLevels';

export const metadata: Metadata = {
  title: 'OrganizationLevels',
};

function Page() {
  return <OrgLevels />;
}

export default Page;
