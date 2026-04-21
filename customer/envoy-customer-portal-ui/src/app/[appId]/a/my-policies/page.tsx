import { Metadata } from 'next';
import React from 'react';
import MyPolicies from './_utils/components/MyPolicies';

export const metadata: Metadata = {
  title: 'My Policies',
};

function Page() {
  return <MyPolicies />;
}

export default Page;
