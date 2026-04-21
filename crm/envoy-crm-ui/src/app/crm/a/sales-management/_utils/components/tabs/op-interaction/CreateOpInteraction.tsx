import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useEffect, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams } from 'next/navigation';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllChannel, fetchAllUsers } from '@/app/crm/a/sales-management/_utils/services';
import { addDocuments, createOpInteraction } from '../../../api-service';
import { initInteractionData } from '../../../model';
import { fileUploader } from '@/helpers/services/storageService';
import { ImageDragAndDrop } from '@/components/others/page-related/uploader/ImageDragAndDrop';
import FilePreviewInput from '@/components/others/page-related/uploader/FilePreviewInput';
import { getCurrentUser } from '@/helpers/services/userService';

function CreateOpInteraction({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const t = useTrans('label.sales_managements,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const params = useParams();
  const opportunityId = params.managementId?.toString() || '';
  const currentUser = getCurrentUser();
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initInteractionData);
  const [resource, setResource] = useState<File | null>(null);
  const [defalutUser, setDefalutUser] = useState({ id: '', display_name: '' });
  const [key, setKey] = useState(0);

  useEffect(() => {
    onFormChange('date', getCurrentDate());
    onFormChange('contact_by_id', currentUser?.id?.toString() || '');
    setDefalutUser({ id: currentUser?.id?.toString() || '', display_name: currentUser?.display_name || '' });
  }, []);

  const getCurrentDate = () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.opportunity_interaction.store);
    setIsFormProcessing(true);

    try {
      const docData = await handleFileUpload();
      const responseData = await createOpInteraction(opportunityId, formData);
      setIsFormProcessing(false);
      if (responseData.status_code === 417) {
        printError(responseData.result, form.opportunity_interaction.store, tBe);
      }
      if (responseData.is_success) {
        if (docData) {
          const entity_id = responseData.result.entity_id;
          await addDocuments(entity_id, docData);
        }

        afterSave();
        toaster.success(tBe(responseData.message));
        setFormData(initInteractionData);
        setKey((prevKey) => prevKey + 1);
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  const handleFileUpload = async () => {
    const formData = new FormData();
    if (!resource) {
      return null;
    }
    formData.append('file', resource);
    const fileName = resource.name;
    const fileExtension = resource.name.split('.').pop();
    const key = await fileUploader(formData, 'envoy-test');
    return { doc: key, name: fileName, type: fileExtension };
  };

  return (
    <Modal isOpen={isOpen} onBackdrop={() => onCancel()} size="lg">
      <ModalHeader title={t('add_new_interaction')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.opportunity_interaction.store}`} key={key}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Input isRequired label={t('date')} value={formData.date} onChange={(e) => onFormChange('date', e.target.value)} className="form-control error-date" name="date" type="date" />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="contacts" label={t('contacts')} />
              <AsyncSelect
                onChange={(value) => onFormChange('contact_by_id', value)}
                className="form-control error-contact_by_id"
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllUsers(searchValue, currentPage)}
                defaultValue={defalutUser}
                option={{
                  // labelFn: (option) => (
                  //   <>
                  //     <ProfileInfo title={option.display_name} subtitle={option.email} imageKey={option.picture} />
                  //   </>
                  // ),
                  label: 'display_name',
                  value: 'id',
                }}
              />
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
            <div className="col-12 col-md-6 mb-3">
              <Input type="textarea" label={t('remarks')} value={formData.notes} onChange={(e) => onFormChange('notes', e.target.value)} className="form-control error-notes" name="notes" />
            </div>
            <div className="col-12 mb-3">
              <Label label={t('resources')} />
              {!resource ? (
                <ImageDragAndDrop maxSize={25} htmlFor={'document'} selectedImage={(file: File) => setResource(file)} className="form-control error-coverage_details" />
              ) : (
                <FilePreviewInput fileName={resource.name} onCancel={() => setResource(null)} />
              )}
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

export default CreateOpInteraction;
