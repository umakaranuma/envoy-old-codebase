import React from 'react';
import { ProductCategoriesView } from '../_utils/components/ProductCategoriesView';
import { Metadata } from 'next';
import { SearchParams } from 'next/dist/server/request/search-params';

export const metadata: Metadata = {
  title: 'Product Categories',
};

async function Page({ searchParams }: { searchParams: Promise<SearchParams> }) {
  const sp = await searchParams;
  const backURL = sp?.backUrl;

  return <ProductCategoriesView backURL={backURL?.toString() || ''} />;
}

export default Page;
