'use client';
import PageHeading from '@/components/others/PageHeading';
import { useTrans } from '@/helpers/services/lang/langService';
import React, { useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { deleteProductItem } from '../api-service';
import ProductItemList from './ProductItemList';
import { CreateProductItem } from './CreateProductItem';
import { EditProductItem } from './EditProductItem';
import { ViewProductItem } from './ViewProductItem';

function ProductItems() {
  const t = useTrans('label.product_item,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [tableVers, setTableVers] = useState(0);
  const [createFormKey, setCreateFormKey] = useState(0);
  const [currentEditId, setCurrentEditId] = useState('');
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [currentViewId, setCurrentViewId] = useState('');

  const reloadTable = () => {
    setTableVers((prevValue) => prevValue + 1);
  };
  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteProductItem(deleteId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      reloadTable();
      callback();
      onClose();
    }
  };

  const handleCreateFormCancel = () => {
    setIsCreateOpen(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterSave = () => {
    handleCreateFormCancel();
    reloadTable();
  };

  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('product_items')} icon="core" />
        <div className="d-flex flex-row justify-content-end align-items-center gap-3">
          <Button className="d-flex align-items-center gap-1" onClick={() => setIsCreateOpen(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('add_new_entity', { entity: t('product_item') })}</span>
          </Button>
          {/* <Dropdown
                        trigger={
                            <Button color="primary" variant="outline" className="d-flex align-items-center gap-1">
                                <Flexicon icon="dots-vertical" variant="line" size={15} />
                            </Button>
                        }
                    >
                        {(onClose: Function) => (
                            <>
                                <DropdownItem onClick={() => onClose()}>
                                    <div className="d-flex align-items-center gap-2">
                                        <Flexicon icon="download-cloud-02" variant="line" size={14} />
                                        <span>{t('export')}</span>
                                    </div>
                                </DropdownItem>
                            </>
                        )}
                    </Dropdown> */}
        </div>
      </div>
      <ProductItemList tableVers={tableVers} onView={(id: any) => setCurrentViewId(id)} onEdit={(id: any) => setCurrentEditId(id)} handleOnDelete={handleOnDelete} />
      {isCreateOpen && <CreateProductItem key={createFormKey} isOpen={isCreateOpen} onCancel={handleCreateFormCancel} afterSave={handleAfterSave} />}
      {currentEditId !== '' && <EditProductItem isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterEdit={reloadTable} editId={currentEditId} />}
      {currentViewId !== '' && <ViewProductItem isOpen={currentViewId !== ''} onCancel={() => setCurrentViewId('')} viewId={currentViewId} />}
    </>
  );
}

export default ProductItems;
