import React from 'react';
import { Metadata } from 'next';
import { TemplateView } from '../_utils/components/TemplateView';

export const metadata: Metadata = {
  title: 'Templates',
};

function Page() {
  return <TemplateView />;
}

export default Page;
