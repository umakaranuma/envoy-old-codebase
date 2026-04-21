import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { toaster } from '@/helpers/services/toaster';
import { initProductItem } from '../../../../modal';
import { createInsurerProductItem } from '../../../../api-service';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllCategories } from '../../../../services';

function ProductItemCreate({ isOpen, onCancel, afterSave, productId }: { isOpen: boolean; onCancel: Function; afterSave: Function; productId: string }) {
  const t = useTrans('label.products,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initProductItem);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.coverage.store);
    setIsFormProcessing(true);

    try {
      // const apiData = { coverages: [formData] };
      const responseData = await createInsurerProductItem(productId, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.coverage.store, tBe);
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
    <Modal isOpen={isOpen} onBackdrop={() => onCancel()}>
      <ModalHeader title={t('add_new_product_item')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.coverage.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              <Label label={t('title')} isRequired />
              <Input type="text" value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 mb-3 custom-select">
              <Label label={t('category')} isRequired />
              <AsyncSelect
                onChange={(value) => onFormChange('type_id', value)}
                className="form-control error-type_id"
                option={{ label: 'title', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllCategories(searchValue, currentPage)}
              />
            </div>
            <div className="col-12 mb-3">
              <Label label={t('description')} />
              <Input type="textarea" value={formData.description} onChange={(e) => onFormChange('description', e.target.value)} className="form-control error-description" name="description" />
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('create')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default ProductItemCreate;
