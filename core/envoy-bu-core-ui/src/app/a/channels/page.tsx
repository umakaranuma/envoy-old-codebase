import React from 'react';
import Channels from './_utils/components/Channels';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Channels',
};

function page() {
  return <Channels />;
}

export default page;
