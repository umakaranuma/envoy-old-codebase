import React from 'react';
import { Metadata } from 'next';
import Roles from './_utils/components/Roles';

export const metadata: Metadata = {
  title: 'Roles',
};

async function RolesPage() {
  return (
    <>
      <Roles />
    </>
  );
}

export default RolesPage;
