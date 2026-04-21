import React from 'react';
import { Metadata } from 'next';
import { SalesManagementsView } from '../_utils/components/SalesManagementsView';

export const metadata: Metadata = {
  title: 'Sales Managements',
};

async function SalesPage() {
  return <SalesManagementsView />;
}

export default SalesPage;
