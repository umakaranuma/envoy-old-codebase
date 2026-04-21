import React from 'react';
import { Metadata } from 'next';
import ProductCategories from './_utils/components/ProductCategories';

export const metadata: Metadata = {
  title: 'Product Categories',
};

async function SamplePg() {
  return <ProductCategories />;
}

export default SamplePg;
