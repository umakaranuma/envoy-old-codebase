'use client';

import { Button } from '@apptimus-ui/ui-element';
import { useState } from 'react';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import PageHeading from '@/components/others/PageHeading';
import { ProductCategoriesEdit } from './ProductCategoriesEdit';
import ProductCategoriesCreate from './ProductCategoriesCreate';
import ProductCategoriesList from './ProductCategoriesList';
import { deleteType } from '../api-service';
import { toaster } from '@/helpers/services/toaster';
import { useRouter } from 'next/navigation';
// import { useRouter } from 'next/navigation';
// import { TypeView } from './TypeView';

function ProductCategories() {
  const [tableVers, setTableVers] = useState(0);
  const [createFormKey, setCreateFormKey] = useState(0);
  const [createFormVisible, setCreateFormVisible] = useState(false);
  // const [currentViewId, setCurrentViewId] = useState('');
  const [currentEditId, setCurrentEditId] = useState('');
  const router = useRouter();

  // console.log(currentViewId);

  const reloadTable = () => {
    setTableVers((prevValue) => prevValue + 1);
  };

  const handleCreateFormOnCancel = () => {
    setCreateFormVisible(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterSave = () => {
    setTableVers((prevTableVers) => prevTableVers + 1);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleAfterUpdate = () => {
    setCurrentEditId('');
    setTableVers((prevTableVers) => prevTableVers + 1);
  };

  const t = useTrans('label.product_categories,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteType(deleteId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      onClose();
      reloadTable();
    }
  };

  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('product_categories')} icon="crm" />
        <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setCreateFormVisible(true)}>
          <Flexicon icon="plus-circle" size={18} />
          <span className="d-none d-sm-inline">{t('add_new_category')}</span>
        </Button>
      </div>

      <ProductCategoriesList
        tableVers={tableVers}
        onView={(id: any) => router.push(`/a/product-categories/${id}`)}
        onEdit={(id: string) => setCurrentEditId(id)}
        onDelete={() => {}}
        handleOnDelete={handleOnDelete}
      />
      {/* <TypeList tableVers={tableVers} onView={(id: any) => router.push(`/crm/a/type/${id}`)}  onEdit={(id: string) => setCurrentEditId(id)} onDelete={()=>{}} handleOnDelete={handleOnDelete} /> */}
      {createFormVisible && <ProductCategoriesCreate key={createFormKey} isOpen={createFormVisible} onCancel={handleCreateFormOnCancel} afterSave={handleAfterSave} />}
      {currentEditId !== '' && <ProductCategoriesEdit editId={currentEditId} isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterUpdate={handleAfterUpdate} />}
    </>
  );
}

export default ProductCategories;
