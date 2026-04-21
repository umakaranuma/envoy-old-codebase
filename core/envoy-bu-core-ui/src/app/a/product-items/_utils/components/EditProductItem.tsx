'use client';
import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { getOneProductItem, updateProductItem } from '../api-service';

export function EditProductItem({ isOpen, onCancel, afterEdit, editId }: { isOpen: boolean; onCancel: Function; afterEdit: Function; editId: string }) {
  const t = useTrans('label.product_item,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({ title: '', description: '' });
  const [skeleton, setSkeleton] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneProductItem(editId);
      if (responseData?.is_success) {
        setFormData(responseData.result);
      }

      setSkeleton(false);
    };

    if (editId) {
      setSkeleton(true);
      fetchData();
    }
  }, [editId]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    clearError(form.product_item.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updateProductItem(editId, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.product_item.update, tBe);
      }

      if (responseData.is_success) {
        onCancel();
        afterEdit();
        setFormData({ title: '', description: '' });
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      setIsFormProcessing(false);
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('edit_entity', { entity: t('product_item') })} onClose={() => onCancel()} />
      <ModalBody>
        <div id={`${form.product_item.update}`} className="row">
          <div className="row mb-4">
            <div className="col-12 mb-2">
              <Label label={t('title')} isRequired />
              {skeleton ? <InputSkeleton /> : <Input value={formData.title} onChange={(e) => onFormChange('title', e.target.value)} className="form-control error-title" name="title" />}
            </div>
            <div className="col-12 mb-2">
              <Label label={t('description')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input value={formData.description} onChange={(e) => onFormChange('description', e.target.value)} className="form-control error-description" name="description" />
              )}
            </div>
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('update')} onClick={onSubmit} width="sm" isLoading={isFormProcessing} />
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}
