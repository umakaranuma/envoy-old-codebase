import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useEffect, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { createInteraction } from '../../api-service';
import { useParams } from 'next/navigation';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllChannel, fetchAllContacts } from '@/app/crm/a/sales-management/_utils/services';
import { initTaskInteractions } from '../../model';
import { addDocuments } from '@/app/crm/a/sales-management/_utils/api-service';
import { getCurrentDate, handleFileUpload } from '@/helpers/services/commonService';
import { ImageDragAndDrop } from '@/components/others/page-related/uploader/ImageDragAndDrop';
import FilePreviewInput from '@/components/others/page-related/uploader/FilePreviewInput';

function CreateInteraction({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const t = useTrans('label.tasks,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initTaskInteractions);
  const [resource, setResource] = useState<File | null>(null);
  const [key, setKey] = useState(0);
  const params = useParams();
  const taskId = params.taskId?.toString() || '';

  useEffect(() => {
    onFormChange('date', getCurrentDate());
  }, []);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.interaction.store);
    setIsFormProcessing(true);

    try {
      const docData = await handleFileUpload(resource);
      const responseData = await createInteraction(taskId, formData);
      setIsFormProcessing(false);
      if (responseData.status_code === 417) {
        printError(responseData.result, form.interaction.store, tBe);
      }
      if (responseData.is_success) {
        if (docData) {
          const entity_id = responseData.result.entity_id;
          await addDocuments(entity_id, { doc: docData.key, name: docData.type, type: docData.name });
        }

        afterSave();
        toaster.success(tBe(responseData.message));
        setFormData(initTaskInteractions);
        setKey((prevKey) => prevKey + 1);
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('add_new_task_interactions')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.interaction.store}`} key={key}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Input isRequired label={t('date')} value={formData.date} onChange={(e) => onFormChange('date', e.target.value)} className="form-control error-date" name="date" type="date" />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="channel" label={t('channel')} isRequired />
              <AsyncSelect
                onChange={(value) => onFormChange('channel_id', value)}
                className="form-control error-channel_id"
                option={{
                  label: 'name',
                  value: 'id',
                }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllChannel(searchValue, currentPage)}
              />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="contacts" label={t('contacts')} />
              <AsyncSelect
                onChange={(value) => onFormChange('contact_id', value)}
                className="form-control error-contact_id"
                option={{ label: 'name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllContacts(searchValue, currentPage)}
              />
            </div>
            <div className="col-12 mb-3">
              <Label htmlFor="resources" label={t('resources')} />
              {!resource ? (
                <ImageDragAndDrop maxSize={25} htmlFor={'document'} selectedImage={(file: File) => setResource(file)} className="form-control error-resource" />
              ) : (
                <FilePreviewInput fileName={resource.name} onCancel={() => setResource(null)} />
              )}
            </div>
            <div className="col-12 col-md-12 mb-3">
              <Input type="textarea" label={t('remarks')} value={formData.notes} onChange={(e) => onFormChange('notes', e.target.value)} className="form-control error-notes" name="notes" />
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

export default CreateInteraction;
