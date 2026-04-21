'use client';
import React, { useEffect, useState } from 'react';
import { getAllCustomersHierarchies } from '../../api-service';
import { ICustomersHierarchy } from '../../model';
import { useParams, useRouter } from 'next/navigation';
import { useTrans } from '@/helpers/services/lang/langService';
import HierarchyTreeView from './HierarchyTreeView';
import GoBack from '@/components/others/page-related/GoBack';

const Hierarchy = () => {
  const [data, setData] = useState<ICustomersHierarchy | null>(null);
  const [name, setName] = useState<string | undefined>(undefined);
  const [type, setType] = useState<string | undefined>(undefined);
  const { accountId } = useParams();
  const t = useTrans('label.accounts,otr.common,be.msg');
  const [skeleton, setSkeleton] = useState(true);
  const router = useRouter();

  const fetchData = async () => {
    try {
      const response = await getAllCustomersHierarchies(accountId as string);
      if (response?.is_success && response.result.length > 0) {
        const rootNode = response.result[0]; // Taking the first item as root
        setData(rootNode);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setSkeleton(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [accountId]);

  useEffect(() => {
    setName(data?.name ?? '');
    setType(data?.type ?? '');
  }, [data]);

  return (
    <>
      <GoBack goTo={() => router.push('/a/accounts')} title={t('account_hierarchy')} skeleton={skeleton} />
      <div className="bg-white custom-card overflow-hidden p-2 px-4 pt-2 rounded-3">
        {data ? <HierarchyTreeView data={data} name={name} type={type} afterNodeCreation={() => fetchData()} id={accountId} /> : <div></div>}
      </div>
    </>
  );
};

export default Hierarchy;
