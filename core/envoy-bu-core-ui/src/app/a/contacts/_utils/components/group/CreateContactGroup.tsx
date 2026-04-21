import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import Table1 from './Table1';
import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { toaster } from '@/helpers/services/toaster';
import { createContactGroup } from '../../api-service';
import { IContactGroup, initCreateGroupFormData } from '../../model';

function CreateContactGroup({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const t = useTrans('label.contacts,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState<IContactGroup>(initCreateGroupFormData);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    clearError(form.contact_group.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createContactGroup(formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.contact_group.store, tBe);
      }

      if (responseData.is_success) {
        onCancel();
        afterSave();
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen} scrollable size="lg" onBackdrop={() => onCancel()}>
      <ModalHeader title={t('add_user_contact_group_details')} onClose={() => onCancel()} />
      <ModalBody>
        <div id={`${form.contact_group.store}`}>
          <div className="row mb-2">
            <div className="col-12 mb-3">
              <Input isRequired label={t('group_name')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 mb-3">
              <Input
                label={t('description')}
                value={formData.description}
                onChange={(e) => onFormChange('description', e.target.value)}
                className="form-control error-description"
                name="description"
                type="textarea"
              />
            </div>
          </div>
          <div className="col-12 mb-3">
            <Label label={t('source_contacts')} isRequired />
            <Table1 selectedValues={(value: any) => onFormChange('contacts', value)} />
            <span className="error-contacts"></span>
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('create_a_group')} onClick={onSubmit} width="sm" isLoading={isFormProcessing} />
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default CreateContactGroup;
