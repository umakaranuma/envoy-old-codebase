'use client';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import React, { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import PendingApprovalList from './tabs/PendingApprovalList';
import RejectedList from './tabs/RejectedList';
import ApprovedList from './tabs/ApprovedList';
import ViewApproved from './ViewApproved';

function Approvals() {
  const [tableVers, _setTableVers] = useState(0);
  const t = useTrans('label.approvals,otr.common,be.msg');
  const router = useRouter();
  const searchParams = useSearchParams();
  const [tab, setTab] = useState('pending');
  const [currentViewId, setCurrentViewId] = useState('');

  useEffect(() => {
    const tab = searchParams.get('t') || 'pending';
    toggleTableTab(tab);
  }, []);

  const toggleTableTab = (activeTab: string) => {
    setTab(activeTab);
    router.push(`/a/approvals?t=${activeTab}`, { scroll: false });
  };

  return (
    <>
      <div className="page-header-breadcrumb custom-page-header mt-2 mb-4">
        <PageHeading title={t('approvals')} icon="core" />
      </div>
      <div className="panel">
        <div className="il-box-tab mb-3">
          <div className={`il-box-tab-item ${tab === 'pending' ? 'active' : ''}`} onClick={() => toggleTableTab('pending')}>
            {t('pending')}
          </div>
          <div className={`il-box-tab-item ${tab === 'approved' ? 'active' : ''}`} onClick={() => toggleTableTab('approved')}>
            {t('approved')}
          </div>
          <div className={`il-box-tab-item ${tab === 'rejected' ? 'active' : ''}`} onClick={() => toggleTableTab('rejected')}>
            {t('rejected')}
          </div>
        </div>
        {tab === 'pending' && (
          <PendingApprovalList
            tableVers={tableVers}
            onView={(approval_id: string) => {
              router.push(`/a/approvals/${approval_id}`);
            }}
          />
        )}
        {tab === 'approved' && (
          <ApprovedList
            onView={(approval_id: string) => {
              setCurrentViewId(approval_id);
            }}
          />
        )}
        {tab === 'rejected' && (
          <RejectedList
            onView={(approval_id: string) => {
              setCurrentViewId(approval_id);
            }}
          />
        )}
        {currentViewId !== '' && <ViewApproved isOpen={currentViewId !== ''} onCancel={() => setCurrentViewId('')} viewId={currentViewId} status={'approved'} />}
      </div>
    </>
  );
}

export default Approvals;
