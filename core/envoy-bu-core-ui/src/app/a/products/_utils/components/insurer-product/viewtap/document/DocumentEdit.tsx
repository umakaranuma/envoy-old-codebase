import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { FormEvent, useEffect, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { IDocument, initDocument } from '../../../../modal';
import { updateInsurerProductDocument } from '../../../../api-service';

export const DocumentEdit = ({ isOpen, currentEditData, afterUpdate, onCancel }: { isOpen: boolean; currentEditData: IDocument; onCancel: Function; afterUpdate: Function }) => {
  const t = useTrans('label.products,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initDocument);

  useEffect(() => {
    const fetchData = async () => {
      const data: IDocument = currentEditData;
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
    clearError(form.product.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updateInsurerProductDocument(currentEditData.id as string, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.product.update, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setFormData(initDocument);
        afterUpdate();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('edit_document_detail')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.product.update}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              <Label label={t('name')} isRequired />
              <Input type="text" value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} placeholder={t('name')} />
            </div>
            <div className="col-12 mb-3">
              <div className="form-check">
                <input type="checkbox" className="form-check-input" checked={formData.is_mandatory} onChange={(e) => onFormChange('is_mandatory', e.target.checked)} />
                <Label label={t('is_mandatory')} />
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
