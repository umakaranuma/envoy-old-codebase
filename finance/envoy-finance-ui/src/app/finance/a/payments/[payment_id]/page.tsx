import React from 'react';
import { Metadata } from 'next';
import PaymentsView from '../_utils/components/PaymentView';

export const metadata: Metadata = {
  title: 'Payments View',
};

function page() {
  return <PaymentsView />;
}

export default page;
