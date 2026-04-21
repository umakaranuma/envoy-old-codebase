import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { FormEvent, useEffect, useState } from 'react';
import { initFormData, IOrgLevel } from '../model';
import { getOneOrgLevel, updateOrgLevel } from '../api-service';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';

export const OrgLevelsEdit = ({ isOpen, editId, afterUpdate, onCancel }: { isOpen: boolean; editId: string; onCancel: Function; afterUpdate: Function }) => {
  const t = useTrans('label.org_levels,otr.common');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);
  const [skeleton, setSkeleton] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setSkeleton(true);

      const responseData = await getOneOrgLevel(editId);
      if (responseData?.is_success) {
        const data: IOrgLevel = responseData.result;
        onFormChange('title', data.title);
        onFormChange('description', data.description);
        onFormChange('level_order', data.level_order);
      }
      setSkeleton(false);
    };

    if (editId) {
      fetchData();
    }
  }, [editId]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  const tBe = useTrans('be.msg,be.error,be.attri');
  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.org_level.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updateOrgLevel(editId, formData);
      setIsFormProcessing(false);
      if (responseData.status_code === 417) {
        printError(responseData.result, form.org_level.update, tBe);
      }
      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setFormData(initFormData);
        afterUpdate();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('edit_organizational_level', { entity: t('org_levels') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.org_level.update}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              <Label htmlFor="level_name" label={t('level_name')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input value={formData.title || ''} onChange={(e) => onFormChange('title', e.target.value)} className="form-control error-title" id="title" name="title" />
              )}
            </div>
            <div className="col-12 mb-3">
              <Label htmlFor="title" label={t('level_order')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  type="number"
                  value={formData.level_order || ''}
                  onChange={(e) => onFormChange('level_order', e.target.value)}
                  className="form-control error-level_order"
                  id="level_order"
                  name="level_order"
                />
              )}
            </div>

            <div className="col-12 mb-3">
              <Label htmlFor="description" label={t('level_description')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.description || ''}
                  onChange={(e) => onFormChange('description', e.target.value)}
                  className="form-control error-description"
                  id="description"
                  name="description"
                  type="textarea"
                  rows={4}
                />
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
