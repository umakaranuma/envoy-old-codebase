import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useEffect, useState } from 'react';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { getOneIssuedPolicyDocument, updateIssuedPolicyDocument } from '../../../../api-service';

function EditPolicyDocument({ isOpen, editId, onCancel, afterSave }: { isOpen: boolean; editId: string; onCancel: Function; afterSave: Function }) {
  const t = useTrans('label.policy_request,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({ notes: '', file_name: '', file_type: '' });
  const [skeleton, setSkeleton] = useState(true);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneIssuedPolicyDocument(editId);
      if (responseData?.is_success) {
        const data = responseData.result;
        onFormChange('notes', data.notes);
        onFormChange('file_name', data.file_name.substring(0, data.file_name.lastIndexOf('.')));
        onFormChange('file_type', data.file_type);
        setSkeleton(false);
      }
    };

    if (editId) {
      setSkeleton(true);
      fetchData();
    }
  }, [editId]);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.payment_crud.store);
    setIsFormProcessing(true);

    try {
      const responseData = await updateIssuedPolicyDocument(editId, { ...formData, file_name: formData.file_name ? formData.file_name + `.${formData.file_type}` : '' });
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.payment_crud.store, tBe);
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
      <ModalHeader title={t('edit_attachment_file')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.payment_crud.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              <Label label={t('file_name')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input value={formData.file_name} onChange={(e) => onFormChange('file_name', e.target.value)} className="form-control error-file_name" name="file_name" />
              )}
            </div>
            <div className="col-12 mb-3">
              <Label label={t('notes')} />
              {skeleton ? <InputSkeleton /> : <Input value={formData.notes || ''} onChange={(e) => onFormChange('notes', e.target.value)} className="form-control error-notes" name="notes" />}
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('submit')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default EditPolicyDocument;
