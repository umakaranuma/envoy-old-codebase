import React from 'react';
import { Metadata } from 'next';
import Claim from './_utils/components/Claim';

export const metadata: Metadata = {
  title: 'Claim CRUD',
};

async function ClaimPg() {
  return <Claim />;
}

export default ClaimPg;
