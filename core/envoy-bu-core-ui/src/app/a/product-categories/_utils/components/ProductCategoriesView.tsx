'use client';
import { useEffect, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { BasicInfo } from './tabs/BasicInfo';
import { getOneType } from '../api-service';
import { IOpportunityType } from '../model';
import Form from './tabs/Form';
import GoBack from '@/components/others/page-related/GoBack';
import { useBreadcrumb } from '@/contexts/BreadcrumbContext';

export const ProductCategoriesView = ({ backURL }: { backURL: string }) => {
  const t = useTrans('label.product_categories,otr.common');
  const [data, setData] = useState({} as IOpportunityType);
  const [skeleton, setSkeleton] = useState(true);
  const [tab, setTab] = useState('basic');
  const searchParams = useSearchParams();
  const router = useRouter();
  const params = useParams();
  const viewId = params.categoryId?.toString() || '';
  const { setCustomBreadcrumb } = useBreadcrumb();

  useEffect(() => {
    setCustomBreadcrumb({
      text: data.title ? data.title : '',
      backurl: '/a/product-categories',
    });
    return () => setCustomBreadcrumb(null);
  }, [data]);

  useEffect(() => {
    const tab = searchParams.get('t') || 'basic';
    toggleTableTab(tab);
  }, [searchParams]);

  const toggleTableTab = (activeTab: string) => {
    setTab(activeTab);
    router.push(`/a/product-categories/${viewId}?t=${activeTab}&backUrl=${encodeURIComponent(backURL)}`, { scroll: false });
  };

  useEffect(() => {
    if (viewId) {
      setSkeleton(true);
      fetchData();
    }
  }, [viewId]);

  const fetchData = async () => {
    const responseData = await getOneType(viewId);
    responseData?.is_success && (setData(responseData.result), setSkeleton(false));
  };

  return (
    <>
      <GoBack goTo={() => router.push(backURL ? backURL : '/a/product-categories')} title={data.title} skeleton={skeleton} />
      <div className="il-box-tab pb-2">
        <div className={`il-box-tab-item ${tab === 'basic' ? 'active' : ''}`} onClick={() => toggleTableTab('basic')}>
          {t('basic_info')}
        </div>
        <div className={`il-box-tab-item ${tab === 'forms' ? 'active' : ''}`} onClick={() => toggleTableTab('forms')}>
          {t('forms')}
        </div>
      </div>
      {tab === 'basic' && <BasicInfo data={data} skeleton={skeleton} onReload={() => fetchData()} />}
      {tab === 'forms' && <Form viewId={viewId} />}
    </>
  );
};
