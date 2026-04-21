'use client';

import React, { useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { deleteInsurerProductCoverage } from '../../../../api-service';
import ProductItemCreate from './ProductItemCreate';
import ProductItemList from './ProductItemList';
import { ProductItemEdit } from './ProductItemEdit';
import { IProductItem } from '../../../../modal';

function ProductItemDetails({ viewId, isView = true, tableVers, setTableVers }: { viewId: string; isView?: boolean; tableVers: number; setTableVers: Function }) {
  const t = useTrans('label.products,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [currentEditData, setCurrentEditData] = useState<IProductItem | null>(null);
  const [createFormKey, setCreateFormKey] = useState(0);
  const [createFormVisible, setCreateFormVisible] = useState(false);

  const handleAfterUpdate = () => {
    setCurrentEditData(null);
    setTableVers((prevTableVers: number) => prevTableVers + 1);
  };

  const handleCreateFormOnCancel = () => {
    setCreateFormVisible(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterSave = () => {
    setCreateFormVisible(false);
    setTableVers((prevTableVers: number) => prevTableVers + 1);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteInsurerProductCoverage(deleteId);
    setLoader(false);

    if (responseData.status_code === 409) {
      toaster.error(tBe(responseData.message));
    }

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      onClose();
      setTableVers((prevTableVers: number) => prevTableVers + 1);
    }
  };

  return (
    <>
      {!isView && (
        <div className="d-flex justify-content-end">
          <Button className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('add_new_product_item')}</span>
          </Button>
        </div>
      )}

      <ProductItemList viewId={viewId} tableVers={tableVers} setCurrentEditData={setCurrentEditData} handleOnDelete={handleOnDelete} isView={isView} />

      {createFormVisible && <ProductItemCreate key={createFormKey} isOpen={createFormVisible} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} productId={viewId} />}
      {currentEditData !== null && <ProductItemEdit currentEditData={currentEditData} isOpen={currentEditData !== null} onCancel={() => setCurrentEditData(null)} afterUpdate={handleAfterUpdate} />}
    </>
  );
}

export default ProductItemDetails;
