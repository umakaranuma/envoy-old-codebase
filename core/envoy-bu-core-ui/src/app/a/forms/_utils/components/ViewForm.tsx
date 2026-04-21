'use client';
import { useEffect, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import { BasicInfo } from './tabs/BasicInfo';
import Attribute from './tabs/Attribute';
import { getOneForm } from '../api-service';
import { IForm } from '../model';
import GoBack from '@/components/others/page-related/GoBack';

export const ViewForm = () => {
  const t = useTrans('label.form,otr.common');
  const [data, setData] = useState({} as IForm);
  const [skeleton, setSkeleton] = useState(true);
  const [tab, setTab] = useState('basic');
  const searchParams = useSearchParams();
  const router = useRouter();
  const params = useParams();
  const viewId = params.id?.toString() || '';

  useEffect(() => {
    const tab = searchParams.get('t') || 'basic';
    toggleTableTab(tab);
  }, [searchParams]);

  const toggleTableTab = (activeTab: string) => {
    setTab(activeTab);
    router.push(`/a/forms/${viewId}?t=${activeTab}`);
  };

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneForm(viewId);
      responseData?.is_success && (setData(responseData.result), setSkeleton(false));
    };

    if (viewId) {
      setSkeleton(true);
      fetchData();
    }
  }, [viewId]);

  return (
    <>
      <GoBack goTo={() => router.push('/a/forms')} title={data.title} skeleton={skeleton} />
      <div className="panel">
        <div className="il-box-tab pb-2">
          <div className={`il-box-tab-item ${tab === 'basic' ? 'active' : ''}`} onClick={() => toggleTableTab('basic')}>
            {t('basic_info')}
          </div>
          <div className={`il-box-tab-item ${tab === 'attribute' ? 'active' : ''}`} onClick={() => toggleTableTab('attribute')}>
            {t('attribute')}
          </div>
        </div>
      </div>
      {tab === 'basic' && <BasicInfo data={data} skeleton={skeleton} />}
      {tab === 'attribute' && <Attribute />}
    </>
  );
};
