import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { FormEvent, useEffect, useState } from 'react';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useParams } from 'next/navigation';
import { IForm, initFormData } from '../../model';
import { getOneForm, updateTypeForm } from '../../api-service';

export const EditForm = ({ isOpen, editId, afterUpdate, onCancel }: { isOpen: boolean; editId: string; onCancel: Function; afterUpdate: Function }) => {
  const t = useTrans('label.product_categories,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);
  const [skeleton, setSkeleton] = useState(true);
  const params = useParams();
  const formId = params.categoryId as string;

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneForm(formId, editId);

      if (responseData?.is_success) {
        const data: IForm = responseData.result;
        onFormChange('title', data.title);
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
    clearError(form.form_crud.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updateTypeForm(formId, editId, formData);
      setIsFormProcessing(false);

      if (responseData.result === 417) {
        printError(responseData.result, form.form_crud.update, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setFormData(initFormData);
        onCancel();
        afterUpdate();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('edit_entity', { entity: t('form') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.form_crud.update}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Label htmlFor="title" label={t('title')} isRequired />
              {skeleton ? <InputSkeleton /> : <Input value={formData.title} onChange={(e) => onFormChange('title', e.target.value)} className="form-control error-title" id="title" name="title" />}
            </div>
            {/* <div className="col-12 col-md-6 mb-3">
              <Label htmlFor="description" label={t('description')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input value={formData.description} onChange={(e) => onFormChange('description', e.target.value)} className="form-control error-description" id="description" name="description" />
              )}
            </div> */}
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
