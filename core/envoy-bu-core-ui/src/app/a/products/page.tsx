import React from 'react';
import { Metadata } from 'next';
import Products from './_utils/components/Products';

export const metadata: Metadata = {
  title: 'Products',
};

function page() {
  return <Products />;
}

export default page;
