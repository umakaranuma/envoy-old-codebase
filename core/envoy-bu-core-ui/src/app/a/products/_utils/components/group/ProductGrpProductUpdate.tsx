import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Label } from '@apptimus-ui/ui-element';
import { FormEvent, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { initProductGroup } from '../../modal';
import { updateProductGroupProduct } from '../../api-service';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchallNativeProducts } from '../../services';

export const ProductGrpProductUpdate = ({ isOpen, editId, afterUpdate, onCancel }: { isOpen: boolean; editId: string; onCancel: Function; afterUpdate: Function }) => {
  const t = useTrans('label.products,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({ product_ids: [] });

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.product.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updateProductGroupProduct(editId, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.product.update, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setFormData(initProductGroup);
        afterUpdate();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('edit_entity', { entity: t('product_group') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.product.update}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              <Label htmlFor="products" label={t('products')} />
              <div className="custom-select">
                <AsyncSelect
                  onChange={(value) => {
                    onFormChange('product_ids', value);
                  }}
                  className="form-control  error-product_ids"
                  option={{ label: 'name', value: 'id' }}
                  isSearchable={true}
                  loadOptions={fetchallNativeProducts}
                  multiple
                />
              </div>
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('update')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
};
