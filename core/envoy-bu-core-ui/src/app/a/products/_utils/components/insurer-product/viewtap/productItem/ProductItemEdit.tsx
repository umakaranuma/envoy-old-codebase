import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { FormEvent, useEffect, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { IProductItem, initProductItem } from '../../../../modal';
import { updateInsurerProductCoverage } from '../../../../api-service';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllCategories } from '../../../../services';

export const ProductItemEdit = ({ isOpen, currentEditData, afterUpdate, onCancel }: { isOpen: boolean; currentEditData: IProductItem; onCancel: Function; afterUpdate: Function }) => {
  const t = useTrans('label.products,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState<IProductItem>(initProductItem);
  const [defaultCategory, setDefaultCategory] = useState({ id: '', title: '' });

  useEffect(() => {
    const fetchData = async () => {
      const data = currentEditData;
      setDefaultCategory({ id: data.type_id, title: data.type });
      setFormData(data);
    };
    if (currentEditData) {
      fetchData();
    }
  }, [currentEditData]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.job_title.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updateInsurerProductCoverage(currentEditData.id as string, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.job_title.update, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setFormData(initProductItem);
        afterUpdate();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen} onBackdrop={() => onCancel()}>
      <ModalHeader title={t('edit_product_item_detail')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.job_title.update}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              <Label label={t('title')} isRequired />
              <Input type="text" value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 mb-3 custom-select">
              <Label label={t('category')} isRequired />
              <AsyncSelect
                onChange={(_, selectedOption) => {
                  if (selectedOption) {
                    onFormChange('type_id', selectedOption.id);
                    onFormChange('type', selectedOption.title);
                    setDefaultCategory(selectedOption);
                  }
                }}
                className="form-control error-type_id"
                option={{ label: 'title', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllCategories(searchValue, currentPage)}
                defaultValue={defaultCategory}
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
            <Button text={t('update')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
};
