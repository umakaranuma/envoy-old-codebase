'use client';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import React, { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import QuotationList from './tabs/QuotationList';
import PolicyList from './tabs/PolicyList';
import PaymentList from './tabs/PaymentList';
import { approveCustomerRequest } from '../api-service';
import { toaster } from '@/helpers/services/toaster';

function CustomerRequests() {
  const t = useTrans('label.customer_request,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const router = useRouter();
  const searchParams = useSearchParams();
  const [tab, setTab] = useState('quotation');
  const [tableVer, setTableVer] = useState(0);

  useEffect(() => {
    const tab = searchParams.get('t') || 'quotation';
    toggleTableTab(tab);
  }, []);

  const toggleTableTab = (activeTab: string) => {
    setTab(activeTab);
    router.push(`/a/customer-requests?t=${activeTab}`, { scroll: false });
  };

  async function onApprove(id: string, type: string) {
    try {
      const responseData = await approveCustomerRequest(id, { type });

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setTableVer((prev) => prev + 1);
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <>
      <div className="page-header-breadcrumb custom-page-header mt-2 mb-4">
        <PageHeading title={t('customer_requests')} icon="core" />
      </div>
      <div className="panel">
        <div className="il-box-tab mb-3">
          <div className={`il-box-tab-item ${tab === 'quotation' ? 'active' : ''}`} onClick={() => toggleTableTab('quotation')}>
            {t('quotation')}
          </div>
          <div className={`il-box-tab-item ${tab === 'policy' ? 'active' : ''}`} onClick={() => toggleTableTab('policy')}>
            {t('policy_requests')}
          </div>
          <div className={`il-box-tab-item ${tab === 'payments' ? 'active' : ''}`} onClick={() => toggleTableTab('payments')}>
            {t('payments')}
          </div>
        </div>
        {tab === 'quotation' && (
          <QuotationList
            onView={(requestId: string) => {
              router.push(`/a/customer-requests/${requestId}`);
            }}
            tableVer={tableVer}
            setCurrentApprovalId={(id: string) => onApprove(id, 'quotation')}
          />
        )}
        {tab === 'policy' && (
          <PolicyList
            onView={(requestId: string) => {
              router.push(`/a/customer-requests/${requestId}`);
            }}
            tableVer={tableVer}
            setCurrentApprovalId={(id: string) => onApprove(id, 'policy')}
          />
        )}
        {tab === 'payments' && <PaymentList />}
        {/* {currentViewId !== '' && <ViewApproved isOpen={currentViewId !== ''} onCancel={() => setCurrentViewId('')} viewId={currentViewId} status={status} />}
         */}
      </div>
    </>
  );
}

export default CustomerRequests;
