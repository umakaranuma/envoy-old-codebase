import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { INotes } from '../../../model';
import { createNotes } from '@/components/others/common/lead/api-service';

function NotesCreate({ isOpen, onCancel, afterSave, entityId }: { isOpen: boolean; onCancel: Function; afterSave: Function; entityId: string }) {
  const t = useTrans('label.issued_policies,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState<INotes>({
    id: '',
    is_high_priority: 0,
    notes: '',
  });

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.opportunity_note.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createNotes(formData, entityId);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.opportunity_note.store, tBe);
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
      <ModalHeader title={t('add_new_notes')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.opportunity_note.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              <Input
                type="textarea"
                rows={3}
                label={t('content')}
                value={formData.notes}
                onChange={(e) => onFormChange('notes', e.target.value)}
                className="form-control error-notes"
                name="notes"
                isRequired
              />
            </div>
            <div className="d-flex gap-2">
              <input
                type="checkbox"
                checked={formData.is_high_priority === 1}
                onChange={(e) => onFormChange('is_high_priority', e.target.checked ? 1 : 0)}
                className="form-check-input error-is_high_priority"
                name="is_high_priority"
              />
              <div>{t('high_priority')}</div>
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

export default NotesCreate;
