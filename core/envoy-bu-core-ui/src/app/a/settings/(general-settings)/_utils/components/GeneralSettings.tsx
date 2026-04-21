'use client';
import React, { useState } from 'react';
import CustomerPortal from './customer-portal/CustomerPortal';
import CommissionConfig from './commission-config/CommissionConfig';
import TasksConfig from './tasks-config/TaskConfig';
import { useTrans } from '@/helpers/services/lang/langService';
import GoBack from '@/components/others/page-related/GoBack';
import { useRouter } from 'next/navigation';
import ApprovalPermissions from './permissions/Permissions';

function GeneralSettings() {
  const t = useTrans('label.general_settings,otr.common');
  const router = useRouter();
  const [activetab, setActiveTab] = useState('customer-portal');

  return (
    <>
      <GoBack goTo={() => router.push('/a/dashboard')} title={t('general_settings')} />
      <div className="panel">
        <div className="il-box-tab">
          <div
            className={`il-box-tab-item ${activetab === 'customer-portal' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('customer-portal');
            }}
          >
            {t('customer_portal')}
          </div>
          <div
            className={`il-box-tab-item ${activetab === 'commission-config' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('commission-config');
            }}
          >
            {t('commission_config')}
          </div>
          <div
            className={`il-box-tab-item  ${activetab === 'task-config' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('task-config');
            }}
          >
            {t('task_config')}
          </div>
          <div
            className={`il-box-tab-item  ${activetab === 'permissions' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('permissions');
            }}
          >
            {t('permissions')}
          </div>
        </div>
        <div className="mt-4">
          {activetab === 'customer-portal' && <CustomerPortal />}
          {activetab === 'commission-config' && <CommissionConfig />}
          {activetab === 'task-config' && <TasksConfig />}
          {activetab === 'permissions' && <ApprovalPermissions />}
        </div>
      </div>
    </>
  );
}

export default GeneralSettings;
