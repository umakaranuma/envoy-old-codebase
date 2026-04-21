import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { initAttributeFormData } from '../../model';
import { createAttributeOfForm } from '../../api-service';
import { useParams } from 'next/navigation';

function CreateAttribute({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const t = useTrans('label.form,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initAttributeFormData);
  const params = useParams();

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.attribute.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createAttributeOfForm(params.id, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.attribute.store, tBe);
      }

      if (responseData.is_success) {
        afterSave();
        setFormData(initAttributeFormData);
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('create_new_entity', { entity: t('attribute') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.attribute.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Input isRequired label={t('title')} value={formData.title} onChange={(e) => onFormChange('title', e.target.value)} className="form-control error-title" name="title" />
            </div>
            {/* <div className="col-12 col-md-6 mb-3">
              <Input
                isRequired
                label={t('type')}
                value={formData.type}
                onChange={(e) => onFormChange('type', e.target.value)}
                className="form-control error-type"
                name="type"
              />
            </div> */}
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('save')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default CreateAttribute;
