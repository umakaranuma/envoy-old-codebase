import React from 'react';
import { Metadata } from 'next';
import { ProductCategoriesView } from '../../_utils/components/create/ProductCategoriesView';

export const metadata: Metadata = {
  title: 'Product Categories',
};

function Page() {
  return <ProductCategoriesView />;
}

export default Page;
