import React, { FormEvent, useEffect, useState } from 'react';
import { INotes } from '../../../model';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label, Skeleton } from '@apptimus-ui/ui-element';
import { useTrans } from '@/helpers/services/lang/langService';
import { form } from '@/constans/Form';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { getOneNotes, updateNotes } from '@/components/others/common/lead/api-service';

function EditNotes({ isOpen, editId, afterUpdate, onCancel, entityId }: { isOpen: boolean; editId: string; onCancel: Function; afterUpdate: Function; entityId: string }) {
  const t = useTrans('label.issued_policies,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({
    id: '',
    is_high_priority: 0,
    notes: '',
  });
  const [skeleton, setSkeleton] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneNotes(entityId, editId);

      if (responseData?.is_success) {
        const data: INotes = responseData.result;
        onFormChange('notes', data.notes);
        onFormChange('is_high_priority', data.is_high_priority);
        setSkeleton(false);
      }
    };

    if (editId) {
      setSkeleton(true);
      fetchData();
    }
  }, [editId]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsFormProcessing(true);

    try {
      const responseData = await updateNotes(entityId, editId, formData);
      setIsFormProcessing(false);

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setFormData({
          id: '',
          is_high_priority: 0,
          notes: '',
        });
        onCancel();
        afterUpdate();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('edit_note')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.opportunity_note.update}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              <Label label={t('content')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input type="textarea" rows={3} value={formData.notes} onChange={(e) => onFormChange('notes', e.target.value)} className="form-control error-notes" id="notes" name="notes" />
              )}
            </div>
            <div className="col-12 col-md-12 mb-3">
              {skeleton ? (
                <Skeleton />
              ) : (
                <div className="d-flex align-items-center gap-2">
                  <input
                    type="checkbox"
                    checked={Boolean(formData?.is_high_priority)}
                    onChange={(e) => onFormChange('is_high_priority', e.target.checked ? 1 : 0)}
                    className="form-check-input error-is_high_priority"
                    id="is_high_priority"
                    name="is_high_priority"
                  />
                  <div>{t('high_priority')}</div>
                </div>
              )}
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('update')} type="submit" width="sm" isLoading={isFormProcessing} disabled={skeleton} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default EditNotes;
