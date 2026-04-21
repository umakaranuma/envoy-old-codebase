'use client';
import React, { useEffect, useState } from 'react';
import { Button } from '@apptimus-ui/ui-element';
import { useTrans } from '@/helpers/services/lang/langService';
import { useRouter, useSearchParams } from 'next/navigation';
import GoBack from '@/components/others/page-related/GoBack';
import SalesTargetCreateContent from './SalesTargetCreateContent';

function SalesTargetCreate() {
  const t = useTrans('label.sales_target,otr.common');
  const router = useRouter();
  const searchParams = useSearchParams();
  const [currentPg, setCurrentPg] = useState('first');
  const [selectedType, setSelectedType] = useState('individual');

  const handleNextPage = () => {
    setCurrentPg('second');
  };

  useEffect(() => {
    const urlTab = searchParams?.get('tab');
    if (urlTab && (urlTab === 'individual' || urlTab === 'sales-team')) {
      setSelectedType(urlTab);
    }
  }, [searchParams]);

  useEffect(() => {
    const newUrl = `/finance/a/sales-target/create?tab=${selectedType}`;
    router.push(newUrl, { scroll: false });
  }, [selectedType]);

  return (
    <div>
      <div>
        <GoBack goTo={() => router.push(`/finance/a/sales-target?tab=${selectedType}`)} title={t('set_new_sales_target')} />
        {currentPg === 'first' && (
          <div className="panel">
            <div className="panel-title">{t('set_new_sales_target')}</div>
            <div className="panel-subtitle text-muted">{t('select_whether_to_set_targets_for_individual_agents_or_sales_teams')}</div>
            <div className="panel-title mt-4">{t('select_target_type')} :</div>
            {/* Selection cards */}
            <div className="row mt-4">
              <div className="col-md-6 mb-3">
                <div className={`card h-100 cursor-pointer ${selectedType === 'individual' ? 'border-primary border-2' : ''}`} onClick={() => setSelectedType('individual')}>
                  <div className="card-body">
                    <div className="custom-radio-card">
                      <input type="radio" id="individual" name="individual" checked={selectedType === 'individual'} className="mt-1" readOnly />
                      <label htmlFor="individual">
                        <div className="panel-title fw-bold">{t('individual_agent')}</div>
                        <div className="panel-title text-muted">{t('set_sales_targets_for_individual_agents')}</div>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
              <div className="col-md-6 mb-3">
                <div className={`card h-100 cursor-pointer ${selectedType === 'sales-team' ? 'border-primary border-2' : ''}`} onClick={() => setSelectedType('sales-team')}>
                  <div className="card-body">
                    <div className="custom-radio-card">
                      <input type="radio" id="grp" name="grp" value="grp" checked={selectedType === 'sales-team'} className="mt-1" readOnly />
                      <label htmlFor="grp" className="custom-radio-content">
                        <div className="panel-title fw-bold">{t('sales_team')}</div>
                        <div className="panel-title text-muted">{t('set_sales_targets_for_sales_teams')}</div>
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="d-flex gap-2 justify-content-end mt-4">
              <Button text={t('cancel')} color="light" width="sm" onClick={() => router.push(`/finance/a/sales-target?tab=${selectedType}`)} />
              <Button text={t('next')} type="button" width="sm" onClick={() => handleNextPage()} />
            </div>
          </div>
        )}
        {currentPg === 'second' && <SalesTargetCreateContent selectedType={selectedType} setCurrentPg={setCurrentPg} />}
      </div>
    </div>
  );
}

export default SalesTargetCreate;
