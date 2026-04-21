import React from 'react';
import type { Metadata } from 'next';
import MyRequests from './_utils/components/MyRequests';

export const metadata: Metadata = {
  title: 'My Requests',
};

function page() {
  return <MyRequests />;
}

export default page;
