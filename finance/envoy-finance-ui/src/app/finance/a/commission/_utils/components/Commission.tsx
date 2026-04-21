'use client';
import React, { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import PageHeading from '@/components/others/PageHeading';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import BrokerageRevenuesList from './BrokerageRevenuesList';
import AgentCommissionList from './AgentCommissionList';
import MyCommissionList from './MyCommissionList';
import MyCommisionCard from './MyCommisionCard';
import { getMyCommissionTotals } from '../api-service';
import { thousandSeparator } from '@/helpers/services/commonService';
import AddSettlement from './AddSettlement';
import CommissionHistory from './CommissionHistory';

const TABS = ['brokerage_revenue', 'agent_commission', 'my_commission', 'commission_history'];

function Commission() {
  const t = useTrans('label.commission,otr.common,be.msg');
  const router = useRouter();
  const searchParams = useSearchParams();
  const [tab, setTab] = useState<string>('brokerage_revenue');
  const [tableVers, setTableVers] = useState(0);
  const [commissionTotals, setCommissionTotals] = useState({
    total_commission_earned: '0.00',
    total_commission_received: '0.00',
    total_commission_pending: '0.00',
  });
  const [currentSettlementId, setCurrentSettlementId] = useState<string>('');
  // Fetch commission totals when tab is my_commission
  useEffect(() => {
    if (tab === 'my_commission') {
      const fetchTotals = async () => {
        try {
          const response = await getMyCommissionTotals({}, true);
          if (response.is_success && response.result) {
            setCommissionTotals(response.result);
          }
        } catch (error) {
          console.error('Error fetching commission totals:', error);
        }
      };
      fetchTotals();
    }
  }, [tab]);

  // Sync tab from URL and fallback to default
  useEffect(() => {
    const urlTab = searchParams?.get('tab') || 'brokerage_revenue';
    if (TABS.includes(urlTab) && urlTab !== tab) {
      setTab(urlTab);
    }
  }, [searchParams]);

  const handleTabClick = (tabName: string) => {
    if (tabName !== tab) {
      setTab(tabName);
      router.push(`/finance/a/commission?tab=${tabName}`);
    }
  };
  const renderTabContent = () => {
    switch (tab) {
      case 'brokerage_revenue':
        return <BrokerageRevenuesList tableVers={0} onView={(id: string) => console.log('View ID:', id)} onEdit={(id: string) => console.log('Edit ID:', id)} handleOnDelete={() => {}} />;
      case 'agent_commission':
        return (
          <AgentCommissionList
            tableVers={tableVers}
            onView={(id: string) => router.push(`/finance/a/commission/${id}`)}
            onEdit={(id: string) => console.log('Edit ID:', id)}
            handleOnDelete={() => {}}
            onSettle={(id: string) => setCurrentSettlementId(id)}
          />
        );
      case 'my_commission':
        return <MyCommissionList tableVers={0} onView={(id: string) => console.log('View ID:', id)} onEdit={(id: string) => console.log('Edit ID:', id)} handleOnDelete={() => {}} />;
      case 'commission_history':
        return <CommissionHistory />;
      default:
        return <div>Invalid Tab</div>;
    }
  };
  return (
    <>
      {/* Header with Button aligned right on larger screens, stacked on mobile */}
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('commission')} icon="core" />
        <div>
          {tab !== 'my_commission' && (
            <Button
              className="d-flex align-items-center gap-1"
              onClick={() => {
                router.push(tab === 'brokerage_revenue' ? '/finance/a/commission/brokerage-com-calculation' : `/finance/a/commission/commission-calculation?tab=${tab}`);
              }}
              labelIcon={<Flexicon icon="calculator" variant="line" size={18} />}
            >
              <span>{t('commission_calculate')}</span>
            </Button>
          )}
        </div>
      </div>

      {/* Main content */}
      <div className="panel mt-4">
        <div className="il-box-tab">
          {TABS.map((key) => (
            <div className={`il-box-tab-item ${tab === key ? 'active' : ''}`} onClick={() => handleTabClick(key)} key={key}>
              {t(key)}
            </div>
          ))}
        </div>
        {/* Commission cards – stack vertically on mobile, horizontal on md+ */}
        {tab === 'my_commission' && (
          <div className="d-flex flex-column flex-md-row gap-0 gap-md-3">
            <MyCommisionCard title={t('total_commission_earned')} amount={thousandSeparator(commissionTotals.total_commission_earned) || '0'} />
            <MyCommisionCard title={t('commission_received')} amount={thousandSeparator(commissionTotals.total_commission_received) || '0'} />
            <MyCommisionCard title={t('commission_pending')} amount={thousandSeparator(commissionTotals.total_commission_pending) || '0'} />
          </div>
        )}
        {renderTabContent()}
      </div>
      {!!currentSettlementId && (
        <AddSettlement
          currentSettlementId={currentSettlementId}
          isOpen={!!currentSettlementId}
          onCancel={() => setCurrentSettlementId('')}
          afterSave={() => {
            setCurrentSettlementId(''), setTableVers((prev) => prev + 1);
          }}
        />
      )}
    </>
  );
}

export default Commission;
