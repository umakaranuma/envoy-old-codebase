'use client';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { deleteCommissionSetup } from '../api-service';
import CommissionSetupList from './CommissionSetupList';
import { useRouter, useSearchParams } from 'next/navigation';

function CommissionSetup() {
  const t = useTrans('label.commission_setup,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const router = useRouter();
  const [tableVers, setTableVers] = useState(0);
  const [activetab, setActiveTab] = useState('individual_product');
  const searchParams = useSearchParams();

  useEffect(() => {
    const tab = searchParams.get('t') || 'individual_product';
    toggleTab(tab);
  }, []);

  const toggleTab = (tab: string) => {
    setActiveTab(tab);
    setTableVers((prev) => prev + 1);
    router.push(`/finance/a/commission-setup?t=${tab}`, { scroll: false });
  };

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteCommissionSetup(deleteId);
    setLoader(false);
    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      onClose();
      setTableVers((prevTableVers) => prevTableVers + 1);
    } else {
      toaster.error(tBe(responseData.message));
    }
  };

  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('commission_setup')} icon="core" />
        <div className="d-flex gap-2">
          <Button
            className="d-flex align-items-center gap-1"
            onClick={() => {
              router.push('/finance/a/commission-setup/commission-setup-upload');
            }}
            size="md"
            color="light"
          >
            <Flexicon icon="upload-01" size={18} />
            <span>{t('import')}</span>
          </Button>
          <Button className="d-flex align-items-center gap-1" onClick={() => router.push(`/finance/a/commission-setup/create?tab=${activetab}`)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('add_new')}</span>
          </Button>
        </div>
      </div>

      <div className="panel mt-4">
        <div className="il-box-tab">
          <div className={`il-box-tab-item ${activetab === 'individual_product' ? 'active' : ''}`} onClick={() => toggleTab('individual_product')}>
            {t('individual_product')}
          </div>
          <div className={`il-box-tab-item ${activetab === 'product_group' ? 'active' : ''}`} onClick={() => toggleTab('product_group')}>
            {t('product_group')}
          </div>
        </div>

        <CommissionSetupList
          tableVers={tableVers}
          onView={(id: string) => {
            router.push(`/finance/a/commission-setup/${id}`);
          }}
          handleOnDelete={handleOnDelete}
          currentTab={activetab}
          onEdit={(id: string) => {
            router.push(`/finance/a/commission-setup/${id}/edit`);
          }}
        />
      </div>
    </>
  );
}

export default CommissionSetup;
