'use client';
import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError } from '@/helpers/handlers/validationErrorHandler';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { initNode } from '../model';

export function EditNode({ isOpen, onCancel, afterEdit, editId }: { isOpen: boolean; onCancel: Function; afterEdit: Function; editId: string }) {
  const t = useTrans('label.org_nodes,otr.common');
  // const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initNode);
  // const [resource, setResource] = useState<File | null>();
  const [skeleton, setSkeleton] = useState(false);
  console.log(afterEdit);

  useEffect(() => {
    // const fetchData = async () => {
    //   const responseData = await getOneNode(editId);
    //   if (responseData?.is_success) {
    //     const data = responseData.result;
    //     setFormData(data);
    //     setSkeleton(false);
    //   }
    // };

    if (editId) {
      setSkeleton(true);
      //   fetchData();
    }
  }, [editId]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    clearError(form.forms.store);
    setIsFormProcessing(true);

    // try {
    //   // const docData = await handleFileUpload();
    //   const responseData = await updatePartner(editId, formData);
    //   setIsFormProcessing(false);

    //   if (responseData.status_code === 417) {
    //     printError(responseData.result, form.partner.update, tBe);
    //   }

    //   if (responseData.is_success) {
    //     if (deletableResource) {
    //       const deleteResponse = await fileRemover(deletableResource);
    //       if (deleteResponse.success) {
    //         setDeletableResource(null);
    //       }
    //     }
    //     onCancel();
    //     afterEdit();
    //     setFormData(initPartner);
    //     toaster.success(tBe(responseData.message));
    //   }
    // } catch (error) {
    //   console.error('An error occurred:', error);
    // }
  }
  // const handleFileUpload = async () => {
  //     const formData = new FormData();
  //     if (!resource) {
  //         return null;
  //     }
  //     formData.append('file', resource);
  //     const fileName = resource.name;
  //     const fileExtension = resource.name.split('.').pop();
  //     const key = await fileUploader(formData, 'envoy-test');
  //     return { doc: key, name: fileName, type: fileExtension };
  // };

  // const handleFileViewer = async (key: string) => {
  //     const file = await fileReceiver({ key });
  //     window.open(file, '_blank');
  // };

  return (
    <Modal isOpen={isOpen} scrollable>
      <ModalHeader title={t('edit_entity', { entity: t('organizational_node') })} onClose={() => onCancel()} />
      <ModalBody>
        <div id={`${form.org_node.update}`}>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('level_name')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input value={formData.level_name || ''} onChange={(e) => onFormChange('level_name', e.target.value)} className="form-control error-name" name="level_name" />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('parent_node')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input value={formData.parent_node_id || ''} onChange={(e) => onFormChange('parent_node_id', e.target.value)} className="form-control error-email" name="parent_node_id" />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('code')} />
              {skeleton ? <InputSkeleton /> : <Input value={formData.code || ''} onChange={(e) => onFormChange('code', e.target.value)} className="form-control error-description" name="code" />}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('node_name')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input value={formData.node_name || ''} onChange={(e) => onFormChange('node_name', e.target.value)} className="form-control error-email" name="node_name" />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('branch_name_code')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input value={formData.branch_name_code || ''} onChange={(e) => onFormChange('branch_name_code', e.target.value)} className="form-control error-email" name="branch_name_code" />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('physical_address')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input value={formData.physical_address || ''} onChange={(e) => onFormChange('physical_address', e.target.value)} className="form-control error-email" name="physical_address" />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('primary_email')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input value={formData.primary_email || ''} onChange={(e) => onFormChange('primary_email', e.target.value)} className="form-control error-email" name="primary_email" />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('contact_number')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input value={formData.contact_number || ''} onChange={(e) => onFormChange('contact_number', e.target.value)} className="form-control error-email" name="contact_number" />
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
