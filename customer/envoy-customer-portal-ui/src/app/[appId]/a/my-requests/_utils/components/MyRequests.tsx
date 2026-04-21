'use client';
import React from 'react';
import MyRequestList from './MyRequestList';
import { useTrans } from '@/helpers/services/lang/langService';

function MyRequests() {
  const t = useTrans('label.my_request,otr.common');
  return (
    <div className="bg-white rounded-2 pt-3 pb-1 px-3">
      <div className="fs-18 fw-semibold mb-3">{t('my_requests')}</div>
      <MyRequestList />
    </div>
  );
}

export default MyRequests;
