'use client';

import { useEffect, useState } from 'react';
import { Button } from '@apptimus-ui/ui-element';
import { useTrans } from '@/helpers/services/lang/langService';
import { deleteProductGroupProduct, deleteProductGroupTeam, getOneProductGroups } from '../../api-service';
import { IProductGroupFormData } from '../../modal';
import GoBack from '@/components/others/page-related/GoBack';
import { useParams, useRouter } from 'next/navigation';
import { ProductGrpTeamUpdate } from './ProductGrpTeamUpdate';
import { Flexicon } from '@apptimus-ui/flexicon';
import { toaster } from '@/helpers/services/toaster';
import { ProductGrpProductUpdate } from './ProductGrpProductUpdate';
import ProductList from './ProductList';
import TeamList from './TeamList';
import { useBreadcrumb } from '@/contexts/BreadcrumbContext';

export const ViewProductGroup = () => {
  const t = useTrans('label.products,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const router = useRouter();
  const params = useParams();
  const { setCustomBreadcrumb } = useBreadcrumb();
  const viewId = params.ProductGroupId as string;
  const [data, setData] = useState<IProductGroupFormData>();
  const [skeleton, setSkeleton] = useState(true);
  const [activetab, setActivetab] = useState('products');
  const [createFormKey, setCreateFormKey] = useState(0);
  const [editFormProductVisible, setEditFormProductVisible] = useState(false);
  const [editFormTeamsVisible, setEditFormTeamsVisible] = useState(false);
  const [tableVers, setTableVers] = useState(0);

  useEffect(() => {
    setCustomBreadcrumb({
      text: t('view'),
      backurl: '/a/products?t=product-group',
    });
    return () => setCustomBreadcrumb(null);
  }, [setCustomBreadcrumb]);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneProductGroups(viewId);
      if (responseData?.is_success) {
        setData(responseData.result[0]);
        setSkeleton(false);
      }
    };

    if (viewId) {
      setSkeleton(true);
      fetchData();
    }
  }, [viewId]);

  const toggleTableTab = (activeTab: string) => {
    setActivetab(activeTab);
  };

  const handleTeamFormOnCancel = () => {
    setEditFormTeamsVisible(false);
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
  };

  const handleTeamAfterSave = () => {
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
    setEditFormTeamsVisible(false);
    setTableVers((prev) => prev + 1);
  };

  const handleProductFormOnCancel = () => {
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
    setEditFormProductVisible(false);
  };

  const handleProductAfterSave = () => {
    setCreateFormKey((prevCreateFormKey) => prevCreateFormKey + 1);
    setEditFormProductVisible(false);
    setTableVers((prev) => prev + 1);
  };

  const handleTeamOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteProductGroupTeam(viewId, deleteId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      setTableVers((prev) => prev + 1);
      callback();
      onClose();
    }
  };

  const handleProductOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteProductGroupProduct(viewId, deleteId);
    setLoader(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      setTableVers((prev) => prev + 1);
      callback();
      onClose();
    }
  };

  return (
    <>
      <GoBack goTo={() => router.push('/a/products?t=product-group')} title={data?.name} skeleton={skeleton} />
      <div className="panel">
        <div className="il-box-tab pb-2 my-3">
          <div className={`il-box-tab-item ${activetab === 'products' ? 'active' : ''}`} onClick={() => toggleTableTab('products')}>
            {t('products')}
          </div>
          <div className={`il-box-tab-item ${activetab === 'teams' ? 'active' : ''}`} onClick={() => toggleTableTab('teams')}>
            {t('teams')}
          </div>
        </div>

        <div className="row">
          {activetab === 'products' && (
            <div className="ps-5 rounded-2">
              <div className="d-flex justify-content-end">
                {
                  <Button className="d-flex align-items-center gap-1" onClick={() => setEditFormProductVisible(true)}>
                    <Flexicon icon="plus-circle" size={18} />
                    <span className="d-none d-sm-inline">{t('add_new_product')}</span>
                  </Button>
                }
              </div>
              <ProductList handleOnDelete={handleProductOnDelete} tableVers={tableVers} />
              {editFormProductVisible && (
                <ProductGrpProductUpdate key={createFormKey} isOpen={editFormProductVisible} onCancel={handleProductFormOnCancel} afterUpdate={handleProductAfterSave} editId={data?.id as string} />
              )}
            </div>
          )}

          {activetab === 'teams' && (
            <div className="ps-5 rounded-2">
              <div className="d-flex justify-content-end">
                {
                  <Button className="d-flex align-items-center gap-1" onClick={() => setEditFormTeamsVisible(true)}>
                    <Flexicon icon="plus-circle" size={18} />
                    <span className="d-none d-sm-inline">{t('add_new_team')}</span>
                  </Button>
                }
              </div>
              <TeamList handleOnDelete={handleTeamOnDelete} tableVers={tableVers} />
              {editFormTeamsVisible && (
                <ProductGrpTeamUpdate key={createFormKey} isOpen={editFormTeamsVisible} onCancel={handleTeamFormOnCancel} afterUpdate={handleTeamAfterSave} editId={data?.id as string} />
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
};
