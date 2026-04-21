import React from 'react';
import { Metadata } from 'next';
import { ApprovalView } from '../_utils/components/ApprovalView';

export const metadata: Metadata = {
  title: 'Approvals',
};

async function Page() {
  return <ApprovalView />;
}

export default Page;
