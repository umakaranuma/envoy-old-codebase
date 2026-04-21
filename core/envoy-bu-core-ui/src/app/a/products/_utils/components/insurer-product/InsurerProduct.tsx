'use client';

import { useRouter } from 'next/navigation';
import InsurerProductList from './InsurerProductList';
import { useState } from 'react';
import { deleteInsurerProduct } from '../../api-service';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import CreatInsurerProduct from './CreatInsurerProduct';

export default function InsurerProduct({ isCreateInsurerProductOpen, setIsCreateInsurerProductOpen }: { isCreateInsurerProductOpen: boolean; setIsCreateInsurerProductOpen: Function }) {
  const router = useRouter();
  const tBe = useTrans('be.msg,be.error');
  const [tableVers, setTableVers] = useState(0);

  const handleView = (id: string) => {
    router.push(`/a/products/insurer-product/${id}`);
  };

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    try {
      setLoader(true);
      const response = await deleteInsurerProduct(deleteId);

      if (response.is_success) {
        toaster.success(tBe(response.message));
        setTableVers((prev) => prev + 1);
        callback();
        onClose();
      } else {
        toaster.error(tBe(response.message));
      }
    } catch (error) {
      console.error('Delete error:', error);
    } finally {
      setLoader(false);
    }
  };

  return (
    <>
      <InsurerProductList tableVers={tableVers} onView={handleView} handleOnDelete={handleOnDelete} />
      {isCreateInsurerProductOpen && (
        <CreatInsurerProduct
          isOpen={isCreateInsurerProductOpen}
          onCancel={() => setIsCreateInsurerProductOpen(false)}
          afterSave={(id: string) => {
            setIsCreateInsurerProductOpen(false);
            router.push(`/products/insurer-product/${id}`);
          }}
        />
      )}
    </>
  );
}
