import React from 'react';
import { ViewNativeProduct } from '../../_utils/components/native-product/ViewNativeProduct';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Native Product',
};

function page() {
  return (
    <>
      <ViewNativeProduct />
    </>
  );
}

export default page;
