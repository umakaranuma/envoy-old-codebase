import React from 'react';
import { Metadata } from 'next';
import JobTitles from './_utils/components/JobTitles';

export const metadata: Metadata = {
  title: 'Job-Titles',
};

function Page() {
  return <JobTitles />;
}

export default Page;
