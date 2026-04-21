import React from 'react';
import Home from './_utils/components/Home';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Home',
};

function page() {
  return <Home />;
}

export default page;
