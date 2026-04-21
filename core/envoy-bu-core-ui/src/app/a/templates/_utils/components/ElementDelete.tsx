import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import 'react-phone-input-2/lib/style.css';
import { deleteElement } from '../api-service';
import { toaster } from '@/helpers/services/toaster';
import { IElement } from '../model';

function ElementDelete({
  isOpen,
  elementId,
  templateId,
  afterDelete,
  onCancel,
  elements,
  selectedElementCategory,
}: {
  isOpen: boolean;
  elementId: string;
  templateId: string;
  onCancel: Function;
  afterDelete: Function;
  elements: IElement[];
  selectedElementCategory: string;
}) {
  const t = useTrans('label.template,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.customres_crud.update);
    setIsFormProcessing(true);
    try {
      let responseData;
      if (selectedElementCategory === 'input_group') {
        const groupElements = elements.filter((el) => el.parent_id === parseInt(elementId));
        // Collect all responses from deleteElement
        await Promise.all(groupElements.map((groupElement) => deleteElement(templateId, groupElement.id.toString())));
        // You can check each groupResponses[i] for errors if needed

        responseData = await deleteElement(templateId, elementId);
      } else {
        responseData = await deleteElement(templateId, elementId);
      }
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.customres_crud.update, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        afterDelete();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen} position="top">
      <ModalHeader title={t('delete_element')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.contact_crud.store}`}>
        <ModalBody>
          <div className="text-center">{t(`do_you_want_to_delete_this_record`)}</div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('delete')} type="submit" width="sm" isLoading={isFormProcessing} color="danger" />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default ElementDelete;
