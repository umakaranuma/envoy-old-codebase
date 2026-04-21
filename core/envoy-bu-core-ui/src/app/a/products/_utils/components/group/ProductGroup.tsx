import React, { useState } from 'react';
import ProductGroupList from './ProductGroupList';
import { deleteProductGroups } from '../../api-service';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { ProductGroupCreate } from './ProductGroupCreate';
import { ProductGroupEdit } from './ProductGroupEdit';
import { useRouter } from 'next/navigation';

function ProductGroup({ createFormVisible, setCreateFormVisible }: { createFormVisible: boolean; setCreateFormVisible: Function }) {
  const t = useTrans('be.msg,be.error');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const router = useRouter();
  const [tableVers, setTableVers] = useState(0);
  const [currentEditId, setCurrentEditId] = useState('');

  const handleDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    try {
      setLoader(true);
      const response = await deleteProductGroups(deleteId);
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
      toaster.error(t('be.error.delete_failed'));
    }
  };

  const handleCreateFormOnCancel = () => {
    setCreateFormVisible(false);
  };

  const handleAfterSave = () => {
    setTableVers((prevTableVers) => prevTableVers + 1);
  };

  const handleAfterUpdate = () => {
    setCurrentEditId('');
    setTableVers((prevTableVers) => prevTableVers + 1);
  };

  return (
    <>
      <ProductGroupList key={tableVers} onView={(id: string) => router.push(`products/group-product/${id}/view`)} handleOnDelete={handleDelete} tableVers={tableVers} />
      {createFormVisible && <ProductGroupCreate isOpen={createFormVisible} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} />}
      {currentEditId !== '' && <ProductGroupEdit editId={currentEditId} isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterUpdate={handleAfterUpdate} />}
    </>
  );
}

export default ProductGroup;
