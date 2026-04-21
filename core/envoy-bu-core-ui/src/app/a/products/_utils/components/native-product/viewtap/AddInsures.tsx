import { form } from '@/constans/Form';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Label } from '@apptimus-ui/ui-element';
import React, { useState, FormEvent } from 'react';
import { Flexicon } from '@apptimus-ui/flexicon';
import { AsyncSelect } from '@apptimus-ui/select';
import { getAllProducts, getAllVendors } from '../../../services';

type InsurerProduct = {
  vendor_id: string;
  product_id: string;
  vendor_name: string;
  product_name: string;
};

type FormData = {
  category_id?: string;
  insurer_products: InsurerProduct[];
};

function AddInsures({
  isCreateTeamOpen,
  setIsCreateTeamOpen,
  onSubmitApi,
  category_id,
}: {
  isCreateTeamOpen: boolean;
  setIsCreateTeamOpen: React.Dispatch<React.SetStateAction<boolean>>;
  onSubmitApi: (data: any) => Promise<any>;
  category_id: string;
}) {
  const t = useTrans('label.products,otr.common');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [error, setError] = useState('');
  const [vendorDefaultValues, setVendorDefaultValues] = useState<Record<number, { name: string; id: string } | null>>({});
  const [formData, setFormData] = useState<FormData>({
    category_id: '',
    insurer_products: [],
  });

  const addInsurerProduct = () => {
    setFormData((prev) => ({
      ...prev,
      insurer_products: [...prev.insurer_products, { vendor_id: '', product_id: '', vendor_name: '', product_name: '' }],
    }));
  };

  const removeInsurerProduct = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      insurer_products: prev.insurer_products.filter((_, i) => i !== index),
    }));
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

  // Handle select changes
  const handleSelectChange = (name: string, value: any, index?: number, data?: any) => {
    if (name === 'vendor_id' && index !== undefined) {
      setFormData((prev) => ({
        ...prev,
        insurer_products: prev.insurer_products.map((item, i) => (i === index ? { ...item, vendor_id: value, vendor_name: data.name, product_id: '', product_name: '' } : item)),
      }));
    } else if (name === 'product_id' && index !== undefined) {
      setFormData((prev) => ({
        ...prev,
        insurer_products: prev.insurer_products.map((item, i) =>
          i === index
            ? {
                ...item,
                product_id: value,
                vendor_id: data?.vendor_id || item.vendor_id,
                vendor_name: data?.insurer || item.vendor_name,
                product_name: data?.name || item.product_name,
              }
            : item,
        ),
      }));

      setVendorDefaultValues((prev) => ({
        ...prev,
        [index]: {
          name: data?.insurer || '',
          id: data?.vendor_id || '',
        },
      }));
    }
  };

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setIsFormProcessing(true);

    try {
      const response = await onSubmitApi({
        insurer_products: formData.insurer_products,
      });

      if (response?.is_success) {
        setIsCreateTeamOpen(false);
        setFormData({ category_id: '', insurer_products: [] });
      } else if (response?.status_code === 417) {
        setError('the_insurer_product_field_is_required');
      }
    } catch (error) {
      setError('submit_error');
    } finally {
      setIsFormProcessing(false);
    }
  }

  return (
    <div>
      <Modal isOpen={isCreateTeamOpen} onBackdrop={() => setIsCreateTeamOpen(false)}>
        <ModalHeader title={t('add_new_team', { entity: t('product') })} onClose={() => setIsCreateTeamOpen(false)} />
        <form onSubmit={onSubmit} id={`${form.product.store}`}>
          <ModalBody>
            <div className="col-12">
              <h5 className="mb-3">{t('insurer_products')}</h5>
              {error && <div className="text-danger fw-semibold my-2">{t(error)}</div>}
              {formData.insurer_products.map((insurerProduct, index) => (
                <div key={index} className="card mb-3">
                  <div className="card-body">
                    <div className="d-flex justify-content-between mb-3">
                      <h6>{t('insurer_product')}</h6>
                      <Button text={t('delete')} color="danger" width="sm" onClick={() => removeInsurerProduct(index)} />
                    </div>
                    <div className="row">
                      <div className="col-12 col-md-6 mb-3">
                        <Label label={t('insurer_info')} isRequired />
                        <AsyncSelect
                          defaultValue={vendorDefaultValues[index] ? vendorDefaultValues[index] : undefined}
                          onChange={(value: any, data: any) => handleSelectChange('vendor_id', value, index, data)}
                          className={`form-control error-vendor_id`}
                          option={{ label: 'name', value: 'id' }}
                          isSearchable={true}
                          loadOptions={(searchValue, currentPage) => getAllVendors(searchValue, currentPage, category_id)}
                        />
                      </div>
                      <div className="col-12 col-md-6 mb-3">
                        <Label label={t('product_name')} isRequired />
                        <AsyncSelect
                          onChange={(value, data) => {
                            handleSelectChange('product_id', value, index, data);
                          }}
                          className={`form-control error-vendor_id`}
                          option={{ label: 'name', value: 'id' }}
                          isSearchable={true}
                          loadOptions={(searchValue, currentPage) => getAllProducts(searchValue, currentPage, category_id, insurerProduct)}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              ))}

              <Button className="d-flex align-items-center gap-1" onClick={addInsurerProduct} type="button">
                <Flexicon icon="plus-circle" size={18} />
                <span className="">{t('add_new')}</span>
              </Button>
            </div>
          </ModalBody>
          <ModalFooter>
            <div className="d-flex justify-content-end gap-2">
              <Button text={t('create')} type="submit" width="sm" isLoading={isFormProcessing} />
              <Button text={t('cancel')} color="light" width="sm" onClick={() => setIsCreateTeamOpen(false)} />
            </div>
          </ModalFooter>
        </form>
      </Modal>
    </div>
  );
}

export default AddInsures;
