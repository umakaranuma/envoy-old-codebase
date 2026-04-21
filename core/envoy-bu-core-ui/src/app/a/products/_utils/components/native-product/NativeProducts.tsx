import React, { useState } from 'react';
import NativeProductsList from './NativeProductsList';
import { createNativeProduct, deleteNativeProduct } from '../../api-service';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { CreateNativeProduct } from './CreateNativeProduct';
import { useRouter } from 'next/navigation';

function NativeProducts({ isCreateNativeProductOpen, setIsCreateNativeProductOpen }: { isCreateNativeProductOpen: boolean; setIsCreateNativeProductOpen: Function }) {
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [tableVers, setTableVers] = useState(0);
  const router = useRouter();

  const handleCreateSubmit = async (formData: any) => {
    const response = await createNativeProduct(formData);
    if (response.is_success) {
      setTableVers((prev) => prev + 1);
    }
    return response;
  };

  const handleDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    try {
      setLoader(true);
      const response = await deleteNativeProduct(deleteId);
      setLoader(false);

      if (response.is_success) {
        toaster.success(tBe(response.message));
        setTableVers((prev) => prev + 1);
        callback();
        onClose();
      } else {
        toaster.error(tBe(response.message));
      }
    } catch (error) {
      setLoader(false);
      console.error(error);
    }
  };

  return (
    <>
      <NativeProductsList
        key={tableVers}
        onView={(id: string) => router.push(`/a/products/native-product/${id}`)}
        onEdit={(id: string) => router.push(`/a/products/native-product/${id}`)}
        handleOnDelete={handleDelete}
        tableVers={tableVers}
      />
      {isCreateNativeProductOpen && (
        <CreateNativeProduct
          isOpen={isCreateNativeProductOpen}
          onCancel={() => setIsCreateNativeProductOpen(false)}
          onSuccess={() => setTableVers((prev) => prev + 1)}
          onSubmitApi={handleCreateSubmit}
        />
      )}
    </>
  );
}

export default NativeProducts;
