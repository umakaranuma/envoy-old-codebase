import React from 'react';
import { Metadata } from 'next';
import Profile from './_utils/components/Profile';

export const metadata: Metadata = {
  title: 'Profile',
};

function Page() {
  return <Profile />;
}

export default Page;
