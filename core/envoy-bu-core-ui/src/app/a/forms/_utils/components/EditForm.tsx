import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { FormEvent, useEffect, useState } from 'react';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { useTrans } from '@/helpers/services/lang/langService';
import { IForm, initFormData } from '../model';
import { getOneForm, updateForm } from '../api-service';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';

export const EditForm = ({ isOpen, editId, afterUpdate, onCancel }: { isOpen: boolean; editId: string; onCancel: Function; afterUpdate: Function }) => {
  const t = useTrans('label.form,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);
  const [skeleton, setSkeleton] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneForm(editId);

      if (responseData?.is_success) {
        const data: IForm = responseData.result;
        onFormChange('title', data.title);
        onFormChange('description', data.description);
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

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.forms.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updateForm(editId, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.forms.update, tBe);
      }

      if (responseData.is_success) {
        onCancel();
        afterUpdate();
        setFormData(initFormData);
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('edit_entity', { entity: t('form') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.forms.update}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('title')} isRequired />
              {skeleton ? <InputSkeleton /> : <Input value={formData.title} onChange={(e) => onFormChange('title', e.target.value)} className="form-control error-title" name="title" />}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('description')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input value={formData.description || ''} onChange={(e) => onFormChange('description', e.target.value)} className="form-control error-description" name="description" />
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
};
