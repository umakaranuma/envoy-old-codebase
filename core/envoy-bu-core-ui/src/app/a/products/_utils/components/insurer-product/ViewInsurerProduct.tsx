'use client';

import { FormEvent, useEffect, useState } from 'react';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import { getOneInsurerProducts, updateInsurerProducts, updateInsurerProductsNativeProductIds } from '../../api-service';
import { useParams, useRouter } from 'next/navigation';
import GoBack from '@/components/others/page-related/GoBack';
import DocumentDeatils from './viewtap/document/DocumentDeatils';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { form } from '@/constans/Form';
import { AsyncSelect, Select } from '@apptimus-ui/select';
import { fetchAllNativProduct, fetchCurrencies, fetchInsurers, fetchOpportunityTypes } from '../../services';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { fileUploader } from '@/constans/storageService';
import { toaster } from '@/helpers/services/toaster';
import { Flexicon } from '@apptimus-ui/flexicon';
import ProductItemDetails from './viewtap/productItem/ProductItemDetails';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { IInsurerProduct, initInsurerProduct } from '../../modal';
import InputFileUploader from '@/components/others/page-related/uploader/InputFileUploader';
import FilePreviewInput from '@/components/others/page-related/uploader/FilePreviewInput';
import { useBreadcrumb } from '@/contexts/BreadcrumbContext';
import FilePreviewer from '@/components/others/page-related/FilePreviewer';

export const ViewInsurerProduct = () => {
  const t = useTrans('label.products,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const params = useParams();
  const viewId = params.productId?.toString() || '';
  const router = useRouter();
  const { setCustomBreadcrumb } = useBreadcrumb();
  const [formData, setFormData] = useState<IInsurerProduct>(initInsurerProduct);
  const [skeleton, setSkeleton] = useState(true);
  const [activeTab, setActiveTab] = useState<'productItem' | 'documents'>('productItem');
  const [resource, setResource] = useState<{ document_name: string; document_url: string; file?: File }>({ document_name: '', document_url: '' });
  const [isView, setIsView] = useState(true);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [isMapNativeProductFormOpen, setIsMapNativeProductFormOpen] = useState(false);
  const [mapNativeProductIds, setMapNativeProductIds] = useState('');
  const [ProductItemTableVers, setProductItemTableVers] = useState(0);
  const [defaultNativeProduct, setDefaultNativeProduct] = useState<{ name: string; id: string } | null>({ name: '', id: '' });
  const [key, setKey] = useState(0);

  useEffect(() => {
    setCustomBreadcrumb({
      text: formData?.code,
      backurl: '/a/products?t=insurer-product',
    });
    return () => setCustomBreadcrumb(null);
  }, [setCustomBreadcrumb, formData]);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneInsurerProducts(viewId);
      if (responseData?.is_success) {
        setFormData(responseData.result);
        // Initialize resource with existing document data
        setResource({
          document_name: responseData.result.doc_name || '',
          document_url: responseData.result.docs || '',
        });
        setDefaultNativeProduct({ name: responseData.result.native_product?.name || '', id: responseData.result.native_product?.id || '' });
        setSkeleton(false);
      }
    };

    if (viewId) {
      fetchData();
    }
  }, [viewId, key]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  };

  const handleFileUpload = async (file: File) => {
    const formData = new FormData();
    if (!file) {
      return null;
    }
    formData.append('file', file);
    const fileName = file.name;
    const fileExtension = file.name.split('.').pop();
    const key = await fileUploader(formData, 'envoy-test');
    return { doc: key, name: fileName, type: fileExtension };
  };

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.job_title.update);
    setIsFormProcessing(true);

    try {
      const fileData = resource.file ? await handleFileUpload(resource.file) : null;
      const apiFormData = fileData
        ? { ...formData, docs: fileData?.doc, doc_type: fileData?.type, doc_name: fileData?.name }
        : { ...formData, docs: formData.docs, doc_type: formData.doc_type, doc_name: formData.doc_name };
      const responseData = await updateInsurerProducts(viewId, apiFormData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.job_title.update, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setIsView(true);
        setKey((prev) => prev + 1);
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  async function onSubmitNativeProductIds(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.product.store);
    setIsFormProcessing(true);
    try {
      const apiFormData = { native_product_ids: [mapNativeProductIds] };
      const response = await updateInsurerProductsNativeProductIds(viewId, apiFormData);
      if (response?.status_code === 417) {
        printError(response?.result, form.product.store, tBe);
      } else if (response?.is_success) {
        setProductItemTableVers((prevTableVers) => prevTableVers + 1);
        setIsMapNativeProductFormOpen(false);
        setMapNativeProductIds('');
        setKey((prev) => prev + 1);
        toaster.success(tBe(response?.message || ''));
      }
    } catch (error) {
      console.error('Submit error:', error);
    } finally {
      setIsFormProcessing(false);
    }
  }

  return (
    <>
      <div className="d-flex justify-content-between" key={key}>
        <GoBack
          goTo={() => {
            if (window.history.length > 1) {
              router.back();
            } else {
              router.push('/a/products?t=insurer-product');
            }
          }}
          title={t('insurer_product')}
        />
        {!formData.native_product && !skeleton && (
          <Button type="button" className="d-flex align-items-center justify-content-center gap-1" width="sm" onClick={() => setIsMapNativeProductFormOpen(true)}>
            <Flexicon icon={'link-03'} variant="line" size={15} />
            <span className="d-none d-sm-inline">{t('map_to_native_product')}</span>
          </Button>
        )}
      </div>
      <div>
        {isView ? (
          <div className="panel">
            <div className="row">
              <div className="col-12 col-md-4 mb-3">
                <Description label={t('product_code')} value={formData?.code || '-'} skeleton={skeleton} />
              </div>
              <div className="col-12 col-md-4 mb-3">
                <Description label={t('product_name')} value={formData?.name || '-'} skeleton={skeleton} />
              </div>
              <div className="col-12 col-md-4 mb-3">
                <Description label={t('native_product')} value={formData?.native_product?.name || '-'} skeleton={skeleton} />
              </div>
              <div className="col-12 col-md-4 mb-3">
                <Description label={t('risk_type')} value={formData?.type || '-'} skeleton={skeleton} />
              </div>
              <div className="col-12 col-md-4 mb-3">
                <Description label={t('insurer_info')} value={formData?.insurer || '-'} skeleton={skeleton} />
              </div>
              <div className="col-12 col-md-4 mb-3">
                <Description label={t('coverage_level')} value={formData?.coverage_level || '-'} skeleton={skeleton} />
              </div>
              <div className="col-12 col-md-4 mb-3">
                <Description label={t('description')} value={formData?.description || '-'} skeleton={skeleton} />
              </div>
              <div className="col-12 col-md-4 mb-3">
                <Description label={t('currency')} value={formData?.currency || '-'} skeleton={skeleton} />
              </div>
              <div className="col-12 col-md-4 mb-3">
                <Description
                  label={t('terms_conditions')}
                  value={
                    formData.docs ? (
                      <FilePreviewer
                        fileType={formData.doc_type}
                        s3Url={`${process.env.S3CDN}/${formData.docs}`}
                        fileName={'document'}
                        downloadFileName={`${formData.code}-${formData.name}-terms & conditions`}
                      />
                    ) : (
                      '-'
                    )
                  }
                  skeleton={skeleton}
                />
              </div>
              <div className="col-12 col-md-4 mb-3">
                <Description label={t('remarks')} value={formData?.remarks || '-'} skeleton={skeleton} />
              </div>
            </div>
            <div className="d-flex justify-content-end gap-2">
              <Button type="button" className="d-flex align-items-center justify-content-center gap-1" width="sm" onClick={() => setIsView(false)}>
                <Flexicon icon={'edit-05'} variant="line" size={15} />
                <span className="d-none d-sm-inline">{t('edit')}</span>
              </Button>
            </div>
          </div>
        ) : (
          <form onSubmit={onSubmit} id={`${form.job_title.update}`}>
            <div className="panel">
              <div className="row">
                <div className="col-12 col-md-6 mb-3">
                  <Label label={t('product_name')} isRequired />
                  {skeleton ? (
                    <InputSkeleton />
                  ) : (
                    <Input type="text" name="name" value={formData?.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" placeholder={t('product_name')} />
                  )}
                </div>
                <div className="col-12 col-md-6 mb-3  custom-select">
                  <Label label={t('risk_type')} isRequired />
                  {skeleton ? (
                    <InputSkeleton />
                  ) : (
                    <AsyncSelect
                      defaultValue={{ id: formData?.category_id || '', title: formData.type || '' }}
                      onChange={(_, data) => {
                        onFormChange('category_id', data.id);
                        onFormChange('type', data.title);
                      }}
                      className="form-control error-category_id"
                      option={{ label: 'title', value: 'id' }}
                      isSearchable={true}
                      loadOptions={fetchOpportunityTypes}
                    />
                  )}
                </div>

                <div className="col-12 col-md-6 mb-3  custom-select">
                  <Label label={t('insurer_info')} isRequired />
                  {skeleton ? (
                    <InputSkeleton />
                  ) : (
                    <AsyncSelect
                      defaultValue={{ name: formData?.insurer || '', id: formData?.vendor_id || '' }}
                      onChange={(_, data) => {
                        onFormChange('vendor_id', data.id);
                        onFormChange('insurer', data.name);
                      }}
                      className="form-control error-vendor_id"
                      option={{ label: 'name', value: 'id' }}
                      isSearchable={true}
                      loadOptions={fetchInsurers}
                    />
                  )}
                </div>

                <div className="col-12 col-md-6 mb-3 custom-select">
                  <Label label={t('coverage_level')} isRequired />
                  {skeleton ? (
                    <InputSkeleton />
                  ) : (
                    <Select
                      defaultValue={{ id: formData?.coverage_level || '', name: formData?.coverage_level || '' }}
                      onChange={(value) => onFormChange('coverage_level', value)}
                      className="form-control error-coverage_level"
                      option={{ label: 'name', value: 'id' }}
                      isSearchable={true}
                      options={[
                        {
                          id: 'Basic',
                          name: 'Basic',
                        },
                        {
                          id: 'Plus',
                          name: 'Plus',
                        },
                        {
                          id: 'Premium',
                          name: 'Premium',
                        },
                      ]}
                    />
                  )}
                </div>

                <div className="col-12 col-md-6 mb-3">
                  <Label label={t('description')} isRequired />
                  {skeleton ? (
                    <InputSkeleton />
                  ) : (
                    <Input
                      type="textarea"
                      name="description"
                      value={formData?.description}
                      onChange={(e) => onFormChange('description', e.target.value)}
                      placeholder={t('description')}
                      className="form-control error-description"
                      rows={2}
                    />
                  )}
                </div>
                <div className="col-12 col-md-6 mb-3">
                  <Label label={t('remarks')} />
                  {skeleton ? (
                    <InputSkeleton />
                  ) : (
                    <Input
                      type="textarea"
                      name="remarks"
                      value={formData?.remarks}
                      onChange={(e) => onFormChange('remarks', e.target.value)}
                      placeholder={t('remarks')}
                      className="form-control error-remarks"
                      rows={2}
                    />
                  )}
                </div>
                <div className="col-12 col-md-6 mb-3  custom-select">
                  <Label label={t('currency')} isRequired />
                  {skeleton ? (
                    <InputSkeleton />
                  ) : (
                    <AsyncSelect
                      defaultValue={{ id: formData?.currency_id || '', name: formData?.currency || '' }}
                      onChange={(_, data) => {
                        onFormChange('currency_id', data.id);
                        onFormChange('currency', data.name);
                      }}
                      className="form-control error-currency_id"
                      option={{ label: 'name', value: 'id' }}
                      isSearchable={true}
                      loadOptions={fetchCurrencies}
                    />
                  )}
                </div>
                <div className="col-12 col-md-6 mb-3">
                  <Label label={t('last_update_date')} isRequired />
                  {skeleton ? (
                    <InputSkeleton />
                  ) : (
                    <Input
                      type="date"
                      name="date"
                      value={formData?.date}
                      onChange={(e) => onFormChange('date', e.target.value)}
                      placeholder={t('last_update_date')}
                      className="form-control error-date"
                    />
                  )}
                </div>
                <div className="col-12 col-md-6 mb-3 custom-select">
                  <Label label={t('native_product')} />
                  {skeleton ? (
                    <InputSkeleton />
                  ) : (
                    <AsyncSelect
                      onChange={(_, data) => {
                        setDefaultNativeProduct({ name: data.name, id: data.id });
                        onFormChange('native_product_id', data.id);
                      }}
                      className="form-control error-native_product_id"
                      option={{ label: 'name', value: 'id' }}
                      isSearchable={true}
                      defaultValue={{ name: defaultNativeProduct?.name || '', id: defaultNativeProduct?.id || '' }}
                      loadOptions={(searchValue, currentPage) => fetchAllNativProduct(searchValue, currentPage)}
                    />
                  )}
                </div>
                <div className="col-12 col-md-6 mb-3">
                  <Label label={t('terms_conditions')} />
                  {skeleton ? (
                    <InputSkeleton />
                  ) : (
                    <>
                      {!(resource.document_url || resource.document_name) ? (
                        <InputFileUploader
                          data={(file: File) => setResource((prev) => ({ ...prev, document_name: file.name, file: file }))}
                          className="form-control error-invoice_document"
                          name="invoice_document"
                        />
                      ) : (
                        <FilePreviewInput
                          fileName={resource.document_name}
                          onCancel={() => {
                            setResource((prev) => ({ ...prev, document_name: '', document_url: '', file: undefined }));
                            onFormChange('doc_name', '');
                          }}
                        />
                      )}
                    </>
                  )}
                </div>
              </div>
              <div className="d-flex justify-content-end gap-2">
                <Button text={t('update')} type="submit" width="sm" isLoading={isFormProcessing} disabled={skeleton} />
                <Button
                  text={t('cancel')}
                  color="light"
                  width="sm"
                  onClick={() => {
                    setIsView(true);
                  }}
                />
              </div>
            </div>
          </form>
        )}
      </div>

      <div className="panel">
        <div className="il-box-tab">
          <div className={`il-box-tab-item ${activeTab === 'productItem' ? 'active' : ''}`} onClick={() => setActiveTab('productItem')}>
            {t('product_items')}
          </div>
          <div className={`il-box-tab-item ${activeTab === 'documents' ? 'active' : ''}`} onClick={() => setActiveTab('documents')}>
            {t('documents')}
          </div>
        </div>
        {activeTab === 'productItem' && <ProductItemDetails viewId={viewId} isView={false} tableVers={ProductItemTableVers} setTableVers={setProductItemTableVers} />}
        {activeTab === 'documents' && <DocumentDeatils viewId={viewId} isView={false} />}
      </div>

      {isMapNativeProductFormOpen && (
        <Modal isOpen={isMapNativeProductFormOpen}>
          <ModalHeader title={t('map_to_native_product')} onClose={() => setIsMapNativeProductFormOpen(false)} />
          <form onSubmit={onSubmitNativeProductIds} id={`${form.product.store}`}>
            <ModalBody>
              <div className="col-12 col-md-12 mb-3 custom-select">
                <Label htmlFor="team" label={t('select_native_product')} isRequired />
                <AsyncSelect
                  onChange={(value) => setMapNativeProductIds(value)}
                  className="form-control error-native_product_ids"
                  option={{ label: 'name', value: 'id' }}
                  isSearchable={true}
                  loadOptions={(searchValue, currentPage) => fetchAllNativProduct(searchValue, currentPage)}
                />
              </div>
            </ModalBody>
            <ModalFooter>
              <div className="d-flex justify-content-end gap-2">
                <Button text={t('add')} type="submit" width="sm" isLoading={isFormProcessing} />
                <Button text={t('cancel')} color="light" width="sm" onClick={() => setIsMapNativeProductFormOpen(false)} />
              </div>
            </ModalFooter>
          </form>
        </Modal>
      )}
    </>
  );
};
