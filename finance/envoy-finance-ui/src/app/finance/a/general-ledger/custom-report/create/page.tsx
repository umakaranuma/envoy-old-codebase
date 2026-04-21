'use client';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import React, { useState } from 'react';
import SalesReportList from './components/SalesReportList';

export default function page() {
  const t = useTrans('label.sales_report,otr.common,be.msg');
  const [tableVers, _setTableVers] = useState(0);
  return (
    <div>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('sales_report') + '(01/01/2024 - 31/03/2024)'} icon="core" />
      </div>
      <div className="d-flex justify-content-between align-items-center w-100 bg-white p-3 rounded-3 mt-3">
        <div className="fw-bold">{t('sales_report')}</div>
      </div>
      <SalesReportList
        tableVers={tableVers}
        onView={(id: string) => {
          console.log('id', id);
        }}
      />
    </div>
  );
}
