import { useTrans } from '@/helpers/services/lang/langService';
import React, { useState } from 'react';
import { useParams } from 'next/navigation';
import { toaster } from '@/helpers/services/toaster';
import ProductList from './ProductList';
import CreateIProduct from './CreateIProduct';
import { deleteInterestedProduct } from '../../../api-service';

const InterestedProducts = () => {
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [tableVers, setTableVers] = useState(0);
  const params = useParams();
  const opportunityId = params.managementId?.toString() || '';
  const [createFormKey, setCreateFormKey] = useState(0);
  const [createFormVisible, setCreateFormVisible] = useState(false);

  console.log('params', params);

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteInterestedProduct(opportunityId, deleteId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      onClose();
      setTableVers((prevTableVers) => prevTableVers + 1);
    }
  };

  const handleCreateFormOnCancel = () => {
    setCreateFormVisible(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterSave = () => {
    setTableVers((prevTableVers) => prevTableVers + 1);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  return (
    <>
      <div className="d-flex justify-content-end"></div>
      <ProductList tableVers={tableVers} handleOnDelete={handleOnDelete} setCreateFormVisible={setCreateFormVisible} />
      {createFormVisible && <CreateIProduct key={createFormKey} isOpen={createFormVisible} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} />}
    </>
  );
};

export default InterestedProducts;
