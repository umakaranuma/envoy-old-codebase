import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { createInterestedProduct } from '../../../api-service';
import { useParams } from 'next/navigation';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllProducts } from '../../../services';

function CreateIProduct({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const t = useTrans('label.sales_managements,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({ date: new Date().toISOString().split('T')[0], health: '' });
  const params = useParams();
  const opportunityId = params.managementId?.toString() || '';

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.interested_product.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createInterestedProduct(opportunityId, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.interested_product.store, tBe);
      }

      if (responseData.is_success) {
        afterSave();
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('add_new_entity', { entity: t('interested_product') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.interested_product.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="product" label={t('product')} isRequired />
              <AsyncSelect
                onChange={(value: any) => onFormChange('product_id', value)}
                className="error-product_id"
                loadOptions={fetchAllProducts}
                option={{
                  label: 'name',
                  value: 'id',
                }}
              />
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('add')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default CreateIProduct;
