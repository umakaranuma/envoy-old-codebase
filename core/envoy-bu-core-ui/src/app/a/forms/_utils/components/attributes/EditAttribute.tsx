import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { FormEvent, useEffect, useState } from 'react';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { getOneAttribute, updateAttribute } from '../../api-service';
import { useParams } from 'next/navigation';
import { IAttribute, initAttributeFormData } from '../../model';

export const EditAttribute = ({ isOpen, editId, afterUpdate, onCancel }: { isOpen: boolean; editId: string; onCancel: Function; afterUpdate: Function }) => {
  const t = useTrans('label.form,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initAttributeFormData);
  const [skeleton, setSkeleton] = useState(true);
  const params = useParams();
  const formId = params.id as string;

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneAttribute(formId, editId);

      if (responseData?.is_success) {
        const data: IAttribute = responseData.result;
        onFormChange('title', data.title);
        // onFormChange('description', data.description);
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
    clearError(form.attribute.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updateAttribute(formId, editId, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.attribute.update, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setFormData(initAttributeFormData);
        onCancel();
        afterUpdate();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('edit_entity', { entity: t('attribute') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.attribute.update}`}>
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
