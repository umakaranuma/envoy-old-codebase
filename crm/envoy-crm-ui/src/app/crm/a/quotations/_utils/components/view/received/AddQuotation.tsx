'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import { AsyncSelect, Select } from '@apptimus-ui/select';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { initAddQuotation } from '../../../model';
import { ImageDragAndDrop } from '@/components/others/page-related/uploader/ImageDragAndDrop';
import { fetchAllServiceProvidersOfQuotation, fetchAllUsers } from '../../../service';
import { createReceivedDocument } from '../../../api-service';
import { toaster } from '@/helpers/services/toaster';
import { local_storage } from '@/constans/StorageKeys';
import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { handleFileUpload } from '@/helpers/services/commonService';
import FilePreviewInput from '@/components/others/page-related/uploader/FilePreviewInput';
import { IFileData } from '@/components/others/page-related/chat/_utils/model';

function AddQuotation({ isOpen, onCancel, afterSave, quotationId, defaultData }: { isOpen: boolean; onCancel: Function; afterSave: Function; quotationId: string; defaultData?: IFileData }) {
  const t = useTrans('label.quotations,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [formData, setFormData] = useState(initAddQuotation);
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [resource, setResource] = useState<File | null | any>(null);
  const user = getLocalStorage(local_storage.auth_user_info);

  useEffect(() => {
    onFormChange('quotation_id', quotationId);
    onFormChange('service_provider_name', undefined);
    if (defaultData) {
      console.log('defaultData', defaultData);

      onFormChange('total_amount', defaultData.quotation_fields.total_amount);
      onFormChange('received_date', defaultData.quotation_fields.received_date);
      onFormChange('expiry_date', defaultData.quotation_fields.expiry_date);
      onFormChange('service_provider_name', defaultData.quotation_fields.insurer_company_name);
      onFormChange('service_provider_id', defaultData.quotation_fields.insurer_company_id);
      setResource({
        name: defaultData.document_name,
        size: 0,
        type: defaultData.document_type,
      });
    }
  }, [quotationId, defaultData]);
  console.log('defaultData', defaultData);
  useEffect(() => {
    if (user) {
      onFormChange('by_user_id', user.id), onFormChange('by_user_name', user.display_name);
    }
  }, []);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  useEffect(() => {
    onFormChange('by_user_id', user.id);
  }, []);

  async function onSubmit() {
    clearError(form.quotation.store);
    setIsFormProcessing(true);
    try {
      let docData;
      if (!defaultData?.document_url) {
        docData = await handleFileUpload(resource, `quotation_QT${quotationId}`);
      }
      const responseData = await createReceivedDocument({
        ...formData,
        coverage_details: defaultData?.file_key ? defaultData.file_key : docData?.key,
        coverage_details_type: defaultData?.document_type ? defaultData.document_type : docData?.type,
        coverage_details_name: defaultData?.document_name ? defaultData.document_name : docData?.name,
        id: undefined,
        by_user_name: undefined,
        quotation_code: undefined,
        quotation_request_type: undefined,
        quotation_version: undefined,
        remaining_days: undefined,
      });
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.quotation.store, tBe);
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
    <Modal isOpen={isOpen} size="lg" scrollable>
      <ModalHeader title={t('add_new_entity', { entity: t('quotation_details') })} onClose={() => onCancel()} />
      <ModalBody>
        <div className="row" id={`${form.quotation.store}`}>
          <div className="col-12 col-md-6 mb-3 custom-select">
            <Label htmlFor="insurer_company_name" label={t('insurer_company_name')} isRequired />
            <AsyncSelect
              onChange={(value, data) => {
                onFormChange('service_provider_name', data.name);
                onFormChange('service_provider_id', value);
              }}
              className="form-control error-service_provider_id"
              option={{ label: 'name', value: 'service_provider_id' }}
              isSearchable={true}
              loadOptions={(searchValue, currentPage) => fetchAllServiceProvidersOfQuotation(searchValue, currentPage, quotationId)}
              defaultValue={{ name: formData.service_provider_name, service_provider_id: formData.service_provider_id }}
            />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Input
              label={t('received_date')}
              isRequired
              type="date"
              value={formData.received_date || ''}
              onChange={(e) => onFormChange('received_date', e.target.value)}
              className="form-control error-received_date"
              name="received_date"
            />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Input
              label={t('expiry_date')}
              type="date"
              isRequired
              value={formData.expiry_date || ''}
              onChange={(e) => onFormChange('expiry_date', e.target.value)}
              className="form-control error-expiry_date"
              name="expiry_date"
              min={new Date().toISOString().split('T')[0]}
            />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Input
              label={t('quotation_value')}
              isRequired
              value={formData.total_amount || ''}
              onChange={(e) => onFormChange('total_amount', e.target.value)}
              className="form-control error-total_amount"
              name="total_amount"
            />
          </div>
          {/* <div className="col-12 col-md-6 mb-3 custom-select">
            <Label htmlFor="status" label={t('status')} isRequired />
            <Select
              onChange={(value) => onFormChange('status', value)}
              className="form-control error-status"
              option={{ label: 'label', value: 'value' }}
              isSearchable={false}
              options={statusTypes}
              defaultValue={{ label: 'Pending', value: 'PENDING' }}
            />
          </div> */}
          <div className="col-12 col-md-6 mb-3 custom-select">
            <Label htmlFor="revised" label={t('revised')} isRequired />
            <Select
              onChange={(value) => onFormChange('re_request', value)}
              className="form-control error-re_request"
              option={{ label: 'label', value: 'value' }}
              isSearchable={false}
              options={[
                { label: 'Yes', value: 'yes' },
                { label: 'No', value: 'no' },
              ]}
            />
          </div>
          <div className="col-12 col-md-6 mb-3 custom-select">
            <Label htmlFor="uploaded_by" label={t('uploaded_by')} isRequired />
            <AsyncSelect
              onChange={(_value: any, data: any) => {
                onFormChange('by_user_id', data.id), onFormChange('by_user_name', data.display_name);
              }}
              className="form-control error-uploaded_by"
              option={{ label: 'display_name', value: 'id' }}
              defaultValue={{ display_name: formData.by_user_name, id: formData.by_user_id }}
              isSearchable={true}
              loadOptions={(searchValue, currentPage) => fetchAllUsers(searchValue, currentPage)}
            />
          </div>
          <div className="col-12 mb-3">
            <Label htmlFor="request_type" label={t('upload_quotation')} isRequired />

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
          <Button text={t('create')} onClick={onSubmit} width="sm" isLoading={isFormProcessing} />
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default AddQuotation;
