'use client';

import GoBack from '@/components/others/page-related/GoBack';
import { useTrans } from '@/helpers/services/lang/langService';
import { Button } from '@apptimus-ui/ui-element';
import { useRouter, useSearchParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import GroupProductCreate from './GroupProductCreate';
import SingleProductCreate from './SingleProductCreate';
import { useBreadcrumb } from '@/contexts/BreadcrumbContext';

function Page() {
  const t = useTrans('label.commission_setup,label.mapping_data_table_preview,otr.common');
  const { setCustomBreadcrumb } = useBreadcrumb();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [selectedType, setSelectedType] = useState('individual');
  const [currentPg, setcurrentPg] = useState('first');

  useEffect(() => {
    setCustomBreadcrumb({
      text: t('create'),
      backurl: '/finance/a/commission-setup',
    });
    return () => setCustomBreadcrumb(null);
  }, [setCustomBreadcrumb]);

  // Handle tab parameter from URL
  useEffect(() => {
    const tab = searchParams.get('tab');
    if (tab === 'individual_product') {
      setSelectedType('individual');
    } else if (tab === 'product_group') {
      setSelectedType('group');
    }
  }, [searchParams]);

  const handleNextPage = () => {
    setcurrentPg('second');
  };

  return (
    <div>
      <GoBack goTo={() => router.push('/finance/a/commission-setup')} title={t('commission_setup')} />
      {currentPg === 'first' && (
        <div className="panel">
          <div className="panel-title">{t('add_new_commission_rule')}</div>
          <div className="panel-subtitle text-muted">{t('select_whether_this_rule_applies_to_an_individual_product_or_to_a_group_of_products')}</div>
          <div className="panel-title mt-4">{t('select_rule_type')} :</div>
          {/* Selection cards */}
          <div className="row mt-4">
            <div className="col-md-6 mb-3">
              <div className={`card h-100 cursor-pointer ${selectedType === 'individual' ? 'border-primary border-2' : ''}`} onClick={() => setSelectedType('individual')}>
                <div className="card-body">
                  <div className="custom-radio-card">
                    <input type="radio" id="individual" name="individual" checked={selectedType === 'individual'} className="mt-1" readOnly />
                    <label htmlFor="individual">
                      <div className="panel-title fw-bold">{t('individual_product')}</div>
                      <div className="panel-title text-muted">{t('apply_commission_rules_to_one_or_more_products_individually')}</div>
                    </label>
                  </div>
                </div>
              </div>
            </div>
            <div className="col-md-6 mb-3">
              <div className={`card h-100 cursor-pointer ${selectedType === 'group' ? 'border-primary border-2' : ''}`} onClick={() => setSelectedType('group')}>
                <div className="card-body">
                  <div className="custom-radio-card">
                    <input type="radio" id="grp" name="grp" value="grp" checked={selectedType === 'group'} className="mt-1" readOnly />
                    <label htmlFor="grp" className="custom-radio-content">
                      <div className="panel-title fw-bold">{t('product_group')}</div>
                      <div className="panel-title text-muted">{t('apply_a_single_commission_rule_across_a_group_of_products')}</div>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="d-flex gap-2 justify-content-end mt-4">
            <Button text={t('cancel')} color="light" width="sm" onClick={() => router.push('/finance/a/commission-setup')} />
            <Button text={t('next')} type="button" width="sm" onClick={() => handleNextPage()} />
          </div>
        </div>
      )}

      {currentPg === 'second' && selectedType === 'individual' && <SingleProductCreate setcurrentPg={setcurrentPg} currentPg={currentPg} />}

      {currentPg === 'second' && selectedType === 'group' && <GroupProductCreate setcurrentPg={setcurrentPg} currentPg={currentPg} />}
    </div>
  );
}

export default Page;
