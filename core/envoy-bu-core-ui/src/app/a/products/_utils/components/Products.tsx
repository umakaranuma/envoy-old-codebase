'use client';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button } from '@apptimus-ui/ui-element';
import { useRouter, useSearchParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import NativeProducts from './native-product/NativeProducts';
import InsurerProduct from './insurer-product/InsurerProduct';
import ProductGroup from './group/ProductGroup';

function Products() {
  const t = useTrans('label.products,otr.common');
  const [tab, setTab] = useState('native-product');
  const searchParams = useSearchParams();
  const router = useRouter();
  const [isCreateNativeProductOpen, setIsCreateNativeProductOpen] = useState(false);
  const [isCreateInsurerProductOpen, setIsCreateInsurerProductOpen] = useState(false);
  const [isCreateGroupOpen, setIsCreateGroupOpen] = useState(false);

  useEffect(() => {
    const tab = searchParams.get('t') || 'native-product';
    setTab(tab);
  }, []);

  const toggleTableTab = (activeTab: string) => {
    setTab(activeTab);
    router.push(`/a/products?t=${activeTab}`);
  };

  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('products_management')} icon="core" />
        {tab === 'native-product' && (
          <div className="d-flex gap-4 align-items-center">
            <Button className="d-flex align-items-center gap-1" onClick={() => setIsCreateNativeProductOpen(true)}>
              <Flexicon icon="plus-circle" size={18} />
              <span className="d-none d-sm-inline">{t('add_new_product')}</span>
            </Button>
          </div>
        )}
        {tab === 'insurer-product' && (
          <div className="d-flex gap-4 align-items-center">
            <Button className="d-flex align-items-center gap-1" onClick={() => setIsCreateInsurerProductOpen(true)}>
              <Flexicon icon="plus-circle" size={18} />
              <span className="d-none d-sm-inline">{t('add_new_product')}</span>
            </Button>
          </div>
        )}
        {tab === 'product-group' && (
          <div className="d-flex gap-4 align-items-center">
            <Button className="d-flex align-items-center gap-1" onClick={() => setIsCreateGroupOpen(true)}>
              <Flexicon icon="plus-circle" size={18} />
              <span className="d-none d-sm-inline">{t('create_group')}</span>
            </Button>
          </div>
        )}
      </div>
      <div className="panel mt-4">
        <div className="il-box-tab">
          <div className={`il-box-tab-item ${tab === 'native-product' ? 'active' : ''}`} onClick={() => toggleTableTab('native-product')}>
            {t('native_products')}
          </div>
          <div className={`il-box-tab-item ${tab === 'insurer-product' ? 'active' : ''}`} onClick={() => toggleTableTab('insurer-product')}>
            {t('insurer_products')}
          </div>
          <div className={`il-box-tab-item ${tab === 'product-group' ? 'active' : ''}`} onClick={() => toggleTableTab('product-group')}>
            {t('product_group')}
          </div>
        </div>
        {tab === 'native-product' && <NativeProducts setIsCreateNativeProductOpen={setIsCreateNativeProductOpen} isCreateNativeProductOpen={isCreateNativeProductOpen} />}
        {tab === 'insurer-product' && <InsurerProduct isCreateInsurerProductOpen={isCreateInsurerProductOpen} setIsCreateInsurerProductOpen={setIsCreateInsurerProductOpen} />}
        {tab === 'product-group' && <ProductGroup createFormVisible={isCreateGroupOpen} setCreateFormVisible={setIsCreateGroupOpen} />}
      </div>
    </>
  );
}

export default Products;
