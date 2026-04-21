'use client';

import { FormEvent, useEffect, useState } from 'react';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import { getOneNativeProduct, updateNativeProduct } from '../../api-service';
import InsureProduct from './viewtap/InsureProduct';
import Teams from './viewtap/Teams';
import CoverageDetails from './viewtap/CoverageDetails';
import DocumentDeatils from './viewtap/DocumentDeatils';
import GoBack from '@/components/others/page-related/GoBack';
import { useParams, useRouter } from 'next/navigation';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { AsyncSelect } from '@apptimus-ui/select';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { fetchOpportunityTypes } from '../../services';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { formatDate } from '@/helpers/services/commonService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useBreadcrumb } from '@/contexts/BreadcrumbContext';

export const ViewNativeProduct = () => {
  const t = useTrans('label.products,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const params = useParams();
  const router = useRouter();
  const { setCustomBreadcrumb } = useBreadcrumb();
  const viewId = params.nativeProductId as string;
  const [isView, setIsView] = useState(true);
  const [data, setData] = useState<any>(null);
  const [skeleton, setSkeleton] = useState(true);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [activetab, setActivetab] = useState('insurers');
  const [key, setKey] = useState(0);
  const [formData, setFormData] = useState<any>({
    id: '',
    name: '',
    category_id: '',
    insurer_products: [],
    type: '',
    opportunity_type_id: '',
  });

  useEffect(() => {
    setCustomBreadcrumb({
      text: data?.code,
      backurl: '/a/products?t=native-product',
    });
    return () => setCustomBreadcrumb(null);
  }, [setCustomBreadcrumb, data]);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneNativeProduct(viewId);
      if (responseData?.is_success) {
        setData(responseData.result[0]);
        const productData = responseData.result[0];
        const transformedData = {
          id: productData.id,
          name: productData.name,
          category_id: productData?.category_id?.toString(),
          insurer_products: productData?.vendor_products?.map((vp: any) => ({
            vendor_id: vp.added_by?.toString(),
            product_id: vp.id.toString(),
            vendor_name: vp.insurer,
            product_name: vp.name,
          })),
          type: productData.type || '',
          vendor_product_ids: productData.vendor_products.map((vp: any) => vp.id),
          opportunity_type_id: productData?.category_id?.toString() || '',
        };
        setFormData(transformedData);
        setSkeleton(false);
      }
    };

    if (viewId) {
      setSkeleton(true);
      fetchData();
    }
  }, [viewId, key]);

  const toggleTableTab = (activeTab: string) => {
    setActivetab(activeTab);
  };

  const handleCancel = () => {
    router.push('/a/products?t=native-product');
  };

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.product.update);
    setIsFormProcessing(true);

    try {
      const response = await updateNativeProduct(formData?.id, formData);
      setIsFormProcessing(false);
      if (response?.status_code === 417) {
        printError(response?.result, form.product.update, tBe);
      } else if (response?.is_success) {
        toaster.success(tBe(response?.message || ''));
        setIsView(true);
        setKey((prev) => prev + 1);
      }
    } catch (error) {
      console.error('Submit error:', error);
      setIsFormProcessing(false);
    }
  }

  return (
    <>
      <GoBack
        goTo={() => {
          if (window.history.length > 1) {
            router.back();
          } else {
            router.push('/a/products?t=native-product');
          }
        }}
        title={t('native_product')}
      />
      <div className="panel" key={key}>
        {isView ? (
          <div className="row">
            <div className="col-12 col-md-4 mb-3">
              <Description label={t('product_code')} value={data?.code || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Description label={t('product_name')} value={data?.name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Description label={t('risk_type')} value={data?.type || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Description label={t('currency')} value={data?.currency || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Description label={t('added_by')} value={data?.added_by || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <Description label={t('last_updated_date')} value={formatDate(data?.updated_at) || '-'} skeleton={skeleton} />
            </div>
            <div className="d-flex justify-content-end gap-2">
              <Button type="button" className="d-flex align-items-center justify-content-center gap-1" width="sm" onClick={() => setIsView(false)}>
                <Flexicon icon={'edit-05'} variant="line" size={15} />
                <span className="d-none d-sm-inline">{t('edit')}</span>
              </Button>
              <Button
                text={t('cancel')}
                color="light"
                width="sm"
                onClick={() => {
                  router.push('/a/products?t=native-product');
                }}
              />
            </div>
          </div>
        ) : (
          <form onSubmit={onSubmit}>
            <div className="row">
              <div className="col-12 col-md-6 mb-3">
                <Label label={t('product_name')} isRequired />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <Input
                    type="text"
                    name="name"
                    value={formData?.name}
                    onChange={(e) => setFormData((prev: any) => ({ ...prev, name: e.target.value }))}
                    className="form-control error-name"
                    placeholder={t('product_name')}
                  />
                )}
              </div>

              <div className="col-12 col-md-6 mb-3 custom-select">
                <Label label={t('risk_type')} isRequired />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <AsyncSelect
                    defaultValue={{ title: formData?.type, id: formData?.opportunity_type_id }}
                    onChange={(_: any, data: any) => {
                      setFormData((prev: any) => ({
                        ...prev,
                        type: data.title,
                        opportunity_type_id: data.id,
                      }));
                    }}
                    className={`form-control error-vendor_id`}
                    option={{ label: 'title', value: 'id' }}
                    isSearchable={true}
                    loadOptions={fetchOpportunityTypes}
                  />
                )}
              </div>
              <div className="col-12">
                <div className="d-flex justify-content-end gap-2">
                  <Button type="submit" className="d-flex align-items-center justify-content-center gap-1" width="sm" isLoading={isFormProcessing}>
                    <Flexicon icon={'edit-05'} variant="line" size={15} />
                    <span className="d-none d-sm-inline">{t('update')}</span>
                  </Button>
                  <Button text={t('cancel')} color="light" width="sm" onClick={handleCancel} />
                </div>
              </div>
            </div>
          </form>
        )}
      </div>

      <div className="panel">
        <div className="il-box-tab pb-2 my-3">
          {/* <div className={`il-box-tab-item ${activetab === 'coverage-details' ? 'active' : ''}`} onClick={() => toggleTableTab('coverage-details')}>
            {t('coverage_details')}
          </div>
          <div className={`il-box-tab-item ${activetab === 'documents' ? 'active' : ''}`} onClick={() => toggleTableTab('documents')}>
            {t('documents')}
          </div> */}
          <div className={`il-box-tab-item ${activetab === 'insurers' ? 'active' : ''}`} onClick={() => toggleTableTab('insurers')}>
            {t('insurer_products')}
          </div>
          <div className={`il-box-tab-item ${activetab === 'teams' ? 'active' : ''}`} onClick={() => toggleTableTab('teams')}>
            {t('teams')}
          </div>
        </div>

        {activetab === 'insurers' && <InsureProduct viewId={viewId} isEdit={true} />}
        {activetab === 'teams' && <Teams viewId={viewId} isEdit={true} />}
        {activetab === 'coverage-details' && <CoverageDetails viewId={viewId} />}
        {activetab === 'documents' && <DocumentDeatils viewId={viewId} />}
      </div>
    </>
  );
};
