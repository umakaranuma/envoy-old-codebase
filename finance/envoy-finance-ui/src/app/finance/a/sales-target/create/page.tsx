import React from 'react';
import SalesTargetCreate from '../_utils/components/SalesTargetCreate';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Sales Target create',
};

function SalesTargetCreatePg() {
  return (
    <div>
      <SalesTargetCreate />
    </div>
  );
}

export default SalesTargetCreatePg;
