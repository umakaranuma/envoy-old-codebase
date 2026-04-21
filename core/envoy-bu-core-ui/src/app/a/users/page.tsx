import React from 'react';
import Users from './_utils/components/Users';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Users',
};

function UserPage() {
  return <Users />;
}

export default UserPage;
