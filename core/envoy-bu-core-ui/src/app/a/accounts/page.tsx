import React from 'react';
import { Metadata } from 'next';
import Accounts from './_utils/components/Accounts';

export const metadata: Metadata = {
  title: 'Accounts',
};

async function AccountsPage() {
  return <Accounts />;
}

export default AccountsPage;
