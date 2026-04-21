'use client';

import { useTrans } from '@/helpers/services/lang/langService';
import { AsyncSelect } from '@apptimus-ui/select';
import { Button, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useEffect, useState } from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { initUploadDoc } from '../../../model';
import { ImageDragAndDrop } from '@/components/others/page-related/uploader/ImageDragAndDrop';
import { toaster } from '@/helpers/services/toaster';
import { uploadGeneratedDocument } from '../../../api-service';
import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';
import { fetchAllUsers } from '../../../service';
import FilePreviewInput from '@/components/others/page-related/uploader/FilePreviewInput';
import { handleFileUpload } from '@/helpers/services/commonService';

export function UploadDocument({ isOpen, onCancel, afterSave, quotationId }: { isOpen: boolean; onCancel: Function; afterSave: Function; quotationId: string }) {
  const t = useTrans('label.quotations,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [formData, setFormData] = useState(initUploadDoc);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [resource, setResource] = useState<File | null>(null);
  const user = getLocalStorage(local_storage.auth_user_info);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  useEffect(() => {
    if (user) {
      onFormChange('uploaded_by', user.id), onFormChange('uploaded_by_name', user.display_name);
    }
  }, []);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.document.store);
    setIsFormProcessing(true);
    try {
      const docData = await handleFileUpload(resource, `recommendation_doc_QT${quotationId}`);
      const responseData = await uploadGeneratedDocument({ ...formData, doc_link: docData?.key, doc_type: docData?.type, doc_name: docData?.name, quotation_request_id: quotationId });
      setIsFormProcessing(false);
      if (responseData.status_code === 417) {
        printError(responseData.result, form.document.store, tBe);
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
      <ModalHeader title={t('add_new_entity', { entity: t('recommendation_document_details') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.document.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3 custom-select">
              <Label htmlFor="uploaded_by" label={t('uploaded_by')} isRequired />
              <AsyncSelect
                onChange={(_value: any, data: any) => {
                  onFormChange('uploaded_by', data.id), onFormChange('uploaded_by_name', data.display_name);
                }}
                className="form-control error-uploaded_by"
                option={{ label: 'display_name', value: 'id' }}
                defaultValue={{ display_name: formData.uploaded_by_name, id: formData.uploaded_by }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllUsers(searchValue, currentPage)}
              />
            </div>
            <div className="col-12 mb-3">
              <Label htmlFor="upload_document" label={t('upload_document')} isRequired />
              {!resource ? (
                <ImageDragAndDrop maxSize={25} htmlFor={'document'} selectedImage={(file: File) => setResource(file)} className="form-control error-doc_link" />
              ) : (
                <FilePreviewInput fileName={resource.name} onCancel={() => setResource(null)} />
              )}
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
