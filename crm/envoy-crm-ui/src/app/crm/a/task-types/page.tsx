import React from 'react';
import TaskTypes from './_utils/components/TaskTypes';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Task Types',
};

function page() {
  return <TaskTypes />;
}

export default page;
