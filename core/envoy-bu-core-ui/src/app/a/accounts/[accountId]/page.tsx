import React from 'react';
import { AccountsView } from '../_utils/components/AccountsView';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Accounts',
};

function Page() {
  return <AccountsView />;
}

export default Page;
