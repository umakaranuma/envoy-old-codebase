'use client';
import React, { useEffect, useState } from 'react';
import { ICustomersHierarchy } from '../_utils/model';
import HierarchyTreeView from './HierarchyTreeView';
import { Skeleton } from '@apptimus-ui/ui-element';
import { getAllCustomersHierarchies } from '@/app/a/accounts/_utils/api-service';

const HierarchyView = () => {
  const [data, setData] = useState<ICustomersHierarchy | null>(null);
  const [name, setName] = useState<string | undefined>(undefined);
  const [type, setType] = useState<string | undefined>(undefined);
  const [skeleton, setSkeleton] = useState(false);

  const fetchData = async () => {
    setSkeleton(true);
    try {
      const response = await getAllCustomersHierarchies('1');
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
  }, []);

  useEffect(() => {
    setName(data?.name ?? '');
    setType(data?.type ?? '');
  }, [data]);

  return (
    <div className="overflow-hidden p-2 px-4 pt-2 rounded-3">
      {skeleton && <Skeleton width="100%" height="70vh" className="mt-4" />}
      {data ? <HierarchyTreeView data={data} name={name} type={type} afterNodeCreation={() => fetchData()} id={1} /> : <div></div>}
    </div>
  );
};

export default HierarchyView;
