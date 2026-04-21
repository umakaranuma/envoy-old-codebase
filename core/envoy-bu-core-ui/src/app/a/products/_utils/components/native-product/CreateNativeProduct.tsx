import { useState, FormEvent, useEffect } from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { form } from '@/constans/Form';
import { Flexicon } from '@apptimus-ui/flexicon';
import { AsyncSelect } from '@apptimus-ui/select';
import { ApiResponse, FormData } from '../../modal';
import { fetchOpportunityTypes, getAllProducts, getAllVendors } from '../../services';

export const CreateNativeProduct = ({ isOpen, onCancel, onSuccess, onSubmitApi }: { isOpen: boolean; onCancel: () => void; onSuccess: () => void; onSubmitApi: (data: any) => Promise<any> }) => {
  const t = useTrans('label.products,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [formData, setFormData] = useState<FormData>({
    name: '',
    category_id: '',
    insurer_products: [],
    type: '',
    opportunity_type_id: '',
  });
  const formId = form.product.store;
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [error, setError] = useState('');
  const [vendorDefaultValues, setVendorDefaultValues] = useState<Record<number, { name: string; id: string } | null>>({});
  const [keys, setKeys] = useState<number[]>([]);

  useEffect(() => {
    setError('');
    clearError(formId);
  }, [formData.insurer_products]);

  const handleSelectChange = (name: string, value: any, index?: number, data?: any) => {
    if (name === 'category_id') {
      setFormData((prev) => ({
        ...prev,
        [name]: value,
        opportunity_type_id: value,
        insurer_products: [],
      }));
      setVendorDefaultValues({});
    } else if (name === 'vendor_id' && index !== undefined) {
      setFormData((prev) => ({
        ...prev,
        insurer_products: prev.insurer_products.map((item, i) => (i === index ? { ...item, vendor_id: value, vendor_name: data?.name || '', product_id: '', product_name: '' } : item)),
      }));
      setKeys((prev) => prev.map((k, i) => (i === index ? Date.now() + Math.random() : k)));
      setVendorDefaultValues((prev) => ({
        ...prev,
        [index]: {
          name: '',
          id: '',
        },
      }));
    } else if (name === 'product_id' && index !== undefined) {
      const isProductAlreadySelected = formData.insurer_products.some((item, i) => i !== index && item.product_id === value);

      if (isProductAlreadySelected) {
        toaster.error(tBe('product_already_selected'));
        return;
      }
      setFormData((prev) => ({
        ...prev,
        insurer_products: prev.insurer_products.map((item, i) =>
          i === index
            ? {
                ...item,
                product_id: value,
                vendor_id: data.vendor_id || item.vendor_id,
                vendor_name: data.insurer || item.vendor_name,
                product_name: data.name || item.product_name,
              }
            : item,
        ),
      }));

      setVendorDefaultValues((prev) => ({
        ...prev,
        [index]: {
          name: data.insurer || '',
          id: data.vendor_id || '',
        },
      }));
    }
  };

  const addInsurerProduct = () => {
    setFormData((prev) => ({
      ...prev,
      insurer_products: [...prev.insurer_products, { vendor_id: '', product_id: '', vendor_name: '', product_name: '' }],
    }));
    setKeys((prev) => [...prev, Date.now() + Math.random()]);
  };

  const removeInsurerProduct = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      insurer_products: prev.insurer_products.filter((_, i) => i !== index),
    }));
    setKeys((prev) => prev.filter((_, i) => i !== index));
    setVendorDefaultValues((prev) => {
      const newValues: Record<number, { name: string; id: string } | null> = {};
      Object.entries(prev)
        .filter(([key]) => Number(key) !== index)
        .forEach(([key, value]) => {
          const newKey = Number(key) > index ? Number(key) - 1 : Number(key);
          newValues[newKey] = value;
        });
      return newValues;
    });
  };

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    clearError(formId);
    setIsFormProcessing(true);

    try {
      const transformedData = {
        ...formData,
        vendor_product_ids: formData.insurer_products.map((item) => item.product_id).filter((id) => id !== ''),
      };

      const response = await onSubmitApi(transformedData);
      const responseData = response as unknown as ApiResponse<any>;

      setIsFormProcessing(false);

      if (responseData?.status_code === 417) {
        // Check if vendor_product_ids error exists
        const hasVendorProductIdsError = responseData.result?.vendor_product_ids && Array.isArray(responseData.result.vendor_product_ids) && responseData.result.vendor_product_ids.length > 0;

        // Check if there are any indexed errors in insurer_products
        let hasIndexedErrors = false;
        if (responseData.result?.insurer_products) {
          const insurerProductsErrors = responseData.result.insurer_products;
          hasIndexedErrors = Object.keys(insurerProductsErrors).some((key) => key !== '_error' && !isNaN(Number(key)));
        }

        // Handle nested insurer_products errors
        if (responseData.result?.insurer_products) {
          const insurerProductsErrors = responseData.result.insurer_products;

          // Show general error message only if there are NO indexed errors AND NO vendor_product_ids error
          if (insurerProductsErrors._error && !hasIndexedErrors && !hasVendorProductIdsError) {
            setError(tBe(insurerProductsErrors._error));
          }

          // Handle indexed errors (0, 1, 2, etc.)
          if (hasIndexedErrors) {
            Object.keys(insurerProductsErrors).forEach((key) => {
              if (key !== '_error' && !isNaN(Number(key))) {
                const index = Number(key);
                const indexErrors = insurerProductsErrors[key];

                // Process each field error for this specific index
                Object.entries(indexErrors).forEach(([field, errors]: [string, any]) => {
                  const indexedFieldName = `${field}-${index}`;
                  printError({ [indexedFieldName]: errors }, formId, tBe);
                });
              }
            });
          }
        }

        // Handle vendor_product_ids error ONLY if there are NO indexed errors
        if (hasVendorProductIdsError && !hasIndexedErrors) {
          const vendorProductError = responseData.result.vendor_product_ids;
          // Set the error message directly (e.g., "insurer_product_ids_required")
          setError(tBe(vendorProductError[0]));
        }

        // Handle other flat-level errors (excluding insurer_products and vendor_product_ids)
        const otherErrors: any = {};
        Object.entries(responseData.result || {}).forEach(([key, value]) => {
          if (key !== 'insurer_products' && key !== 'vendor_product_ids') {
            otherErrors[key] = value;
          }
        });
        if (Object.keys(otherErrors).length > 0) {
          printError(otherErrors, formId, tBe);
        }
      } else if (responseData?.is_success) {
        toaster.success(tBe(responseData?.message || ''));
        onSuccess();
        onCancel();
      }
    } catch (error) {
      console.error('Submit error:', error);
      setIsFormProcessing(false);
    }
  }

  return (
    <Modal isOpen={isOpen} size="lg">
      <ModalHeader title={t('add_new_entity', { entity: t('native_product_details') })} onClose={onCancel} />
      <form onSubmit={onSubmit} id={formId}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('product_name')} isRequired />
              <Input
                type="text"
                name="name"
                value={formData?.name}
                onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
                className="form-control error-name"
                placeholder={t('product_name')}
              />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('risk_type')} isRequired />
              <AsyncSelect
                defaultValue={{ value: formData?.category_id || '', label: formData?.type || '' }}
                onChange={(value) => handleSelectChange('category_id', value)}
                className={`form-control error-category_id`}
                option={{ label: 'title', value: 'id' }}
                isSearchable={true}
                loadOptions={fetchOpportunityTypes}
              />
            </div>
            <div className="col-12">
              {formData?.category_id && <div className="panel-title">{t('insurer_products')}</div>}
              {error && <div className="err-msg">{error}</div>}
              {formData.insurer_products.map((insurerProduct, index) => (
                <div key={index} className="card mb-3">
                  <div className="card-body">
                    <div className="d-flex justify-content-between mb-3">
                      <div className="panel-subtitle">
                        {t('insurer_product')} {index + 1}
                      </div>
                      <div onClick={() => removeInsurerProduct(index)}>
                        <Flexicon icon="x-close" variant="line" size={18} className="text-danger pointer" />
                      </div>
                    </div>
                    <div className="row">
                      <div className="col-12 col-md-6 mb-3 custom-select">
                        <Label label={t('insurer_info')} isRequired />
                        <AsyncSelect
                          defaultValue={vendorDefaultValues[index] ? vendorDefaultValues[index] : undefined}
                          onChange={(value: any, data: any) => handleSelectChange('vendor_id', value, index, data)}
                          className={`form-control error-vendor_id-${index}`}
                          option={{ label: 'name', value: 'id' }}
                          isSearchable={true}
                          loadOptions={(searchValue, currentPage) => getAllVendors(searchValue, currentPage, formData.category_id)}
                        />
                      </div>
                      <div className="col-12 col-md-6 mb-3 custom-select" key={keys[index]}>
                        <Label label={t('product_name')} isRequired />
                        <AsyncSelect
                          onChange={(value, data) => {
                            handleSelectChange('product_id', value, index, data);
                          }}
                          className={`form-control error-product_id-${index}`}
                          option={{ label: 'name', value: 'id' }}
                          isSearchable={true}
                          loadOptions={(searchValue, currentPage) => getAllProducts(searchValue, currentPage, formData.category_id, insurerProduct)}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              {formData?.category_id && (
                <div className="d-flex justify-content-end">
                  <div onClick={addInsurerProduct} className="d-flex gap-2 align-items-center text-primary pointer">
                    <Flexicon icon="plus" variant="line" size={14} />
                    {t('add_new')}
                  </div>
                </div>
              )}
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('create')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={onCancel} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
};
