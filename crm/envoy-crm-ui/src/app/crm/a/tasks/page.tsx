import React from 'react';
import Tasks from './_utils/components/Tasks';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Task Management',
};

function Page() {
  return <Tasks />;
}

export default Page;
