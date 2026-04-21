import React from 'react';
import Notifications from './_utils/components/Notifications';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Notifications',
};

function Page() {
  return <Notifications />;
}

export default Page;
