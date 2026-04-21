'use client';
import { useEffect, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { BasicInfo } from './tabs/BasicInfo';
import GoTo from '@/components/others/page-related/GoTo';
import Form from './tabs/Form';
import { getOneType } from '../../api-service';
import { IOpportunityType } from '../../model';

export const ProductCategoriesView = () => {
  const t = useTrans('label.risks,otr.common');
  const [data, setData] = useState({} as IOpportunityType);
  const [skeleton, setSkeleton] = useState(true);
  const [tab, setTab] = useState('basic');
  const searchParams = useSearchParams();
  const router = useRouter();
  const params = useParams();
  const viewId = params.categoryId?.toString() || '';

  useEffect(() => {
    const tab = searchParams.get('t') || 'basic';
    toggleTableTab(tab);
  }, [searchParams]);

  const toggleTableTab = (activeTab: string) => {
    setTab(activeTab);
    router.push(`/policy/a/policy-request/risk-configure/${viewId}?t=${activeTab}`);
  };

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneType(viewId);
      responseData?.is_success && (setData(responseData.result), setSkeleton(false));
    };

    if (viewId) {
      setSkeleton(true);
      fetchData();
    }
  }, [viewId]);

  return (
    <>
      <div className="bg-white custom-card overflow-hidden p-2 px-4 pt-2 rounded-2 rounded-bottom-0">
        <GoTo goTo={() => router.push('/policy/a/policy-request/create')} title={data.title} skeleton={skeleton} />
        <div className="il-tab pb-2">
          <div className={`il-tab-item ${tab === 'basic' ? 'active' : ''}`} onClick={() => toggleTableTab('basic')}>
            {t('basic_info')}
          </div>
          <div className={`il-tab-item ${tab === 'forms' ? 'active' : ''}`} onClick={() => toggleTableTab('forms')}>
            {t('forms')}
          </div>
        </div>
      </div>
      {tab === 'basic' && <BasicInfo data={data} skeleton={skeleton} />}
      {tab === 'forms' && <Form viewId={viewId} />}
    </>
  );
};
