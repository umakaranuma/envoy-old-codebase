import React from 'react';
import { ViewProductGroup } from '../../../_utils/components/group/ViewProductGroup';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Product Group',
};

function page() {
  return (
    <div>
      <ViewProductGroup />
    </div>
  );
}

export default page;
