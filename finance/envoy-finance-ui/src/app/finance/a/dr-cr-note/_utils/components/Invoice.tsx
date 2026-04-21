'use client';
import React from 'react';
import InvoiceList from './InvoiceList';
import { useRouter } from 'next/navigation';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';

function Invoice() {
  const router = useRouter();
  const t = useTrans('label.invoice,otr.common,be.msg');

  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('dr_cr_note_management')} icon="core" />
      </div>
      <InvoiceList
        tableVers={0}
        onView={(id: string) => {
          router.push(`/finance/a/dr-cr-note/${id}`);
        }}
      />
    </>
  );
}

export default Invoice;
