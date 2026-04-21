import React from 'react';
import { ViewInsurerProduct } from '../../_utils/components/insurer-product/ViewInsurerProduct';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Insurer Product',
};

function Page() {
  return <ViewInsurerProduct />;
}

export default Page;
