import React from 'react';
import { ViewAssignedTask } from '../_utils/components/assigned-tasks/ViewAssignedTask';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Task Management',
};

function Page() {
  return <ViewAssignedTask />;
}

export default Page;
