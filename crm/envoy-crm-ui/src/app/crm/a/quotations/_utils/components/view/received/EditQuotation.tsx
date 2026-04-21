import { form } from '@/constans/Form';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { AsyncSelect, Select } from '@apptimus-ui/select';
import React, { useEffect, useState } from 'react';
import { initAddQuotation, IReceivedQuotation, statusTypes } from '../../../model';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { fetchAllServiceProvidersOfQuotation, fetchAllUsers } from '../../../service';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { useParams } from 'next/navigation';
import { getOneReceivedQuotation, updateQuotation } from '../../../api-service';
import { toaster } from '@/helpers/services/toaster';
import { fileRemover } from '@/helpers/services/storageService';
import { ImageDragAndDrop } from '@/components/others/page-related/uploader/ImageDragAndDrop';
import FilePreviewInput from '@/components/others/page-related/uploader/FilePreviewInput';
import { handleFileUpload } from '@/helpers/services/commonService';

function EditQuotation({ isOpen, onCancel, editId, afterUpdate }: { isOpen: boolean; onCancel: Function; editId: string; afterUpdate: Function }) {
  const t = useTrans('label.quotations,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [formData, setFormData] = useState<IReceivedQuotation>(initAddQuotation);
  const [_isFormProcessing, setIsFormProcessing] = useState(false);
  const [skeleton, setSkeleton] = useState(false);
  const params = useParams();
  const quotationId = params.quotationId?.toString() || '';
  const [resource, setResource] = useState<File | null>(null);
  const [deletableResource, setDeletableResource] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneReceivedQuotation(editId);
      if (responseData?.is_success) {
        const data = responseData.result;
        setFormData(data);
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

  async function onSubmit() {
    clearError(form.quotation.update);
    setIsFormProcessing(true);

    try {
      console.log('Form Dataaa', formData);
      const documentData = await handleFileUpload(resource, `quotation_QT${quotationId}`);
      const newFormData = documentData ? { ...formData, coverage_details: documentData.key, coverage_details_name: documentData.name, coverage_details_type: documentData.type } : formData;
      const responseData = await updateQuotation(editId, {
        ...newFormData,
        id: undefined,
        by_user_name: undefined,
        quotation_code: undefined,
        quotation_request_type: undefined,
        quotation_version: undefined,
        remaining_days: undefined,
      });
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.quotation.update, tBe);
      }

      if (responseData.is_success) {
        if (deletableResource) {
          const deleteResponse = await fileRemover(deletableResource);
          if (deleteResponse.success) {
            setDeletableResource(null);
          }
        }
        toaster.success(tBe(responseData.message));
        onCancel();
        afterUpdate();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  useEffect(() => {
    console.log('Form Data:', formData);
  }, [formData]);

  return (
    <Modal isOpen={isOpen} size="lg" scrollable>
      <ModalHeader title={t('update_quotation_details')} onClose={() => onCancel()} />
      <ModalBody>
        <div className="row" id={`${form.quotation.update}`}>
          <div className="col-12 col-md-6 mb-3 custom-select">
            <Label htmlFor="insurer_company_name" label={t('insurer_company_name')} isRequired />
            {skeleton ? (
              <InputSkeleton />
            ) : (
              <AsyncSelect
                onChange={(_value: any, data: any) => {
                  onFormChange('service_provider_id', data.service_provider_id);
                  onFormChange('service_provider_name', data.name);
                }}
                className="form-control error-service_provider_id"
                option={{ label: 'name', value: 'service_provider_id' }}
                isSearchable={true}
                defaultValue={{ name: formData.service_provider_name, service_provider_id: formData.service_provider_id }}
                loadOptions={(searchValue, currentPage) => fetchAllServiceProvidersOfQuotation(searchValue, currentPage, quotationId)}
              />
            )}
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Label label={t('received_date')} />
            {skeleton ? (
              <InputSkeleton />
            ) : (
              <Input
                type="date"
                isRequired
                value={formData.received_date || ''}
                onChange={(e) => onFormChange('received_date', e.target.value)}
                className="form-control error-received_date"
                name="received_date"
              />
            )}
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Label label={t('expiry_date')} isRequired />
            {skeleton ? (
              <InputSkeleton />
            ) : (
              <Input
                type="date"
                min={new Date().toISOString().split('T')[0]}
                value={formData.expiry_date || ''}
                onChange={(e) => onFormChange('expiry_date', e.target.value)}
                className="form-control error-expiry_date"
                name="expiry_date"
              />
            )}
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Label label={t('quotation_value')} isRequired />
            {skeleton ? (
              <InputSkeleton />
            ) : (
              <Input value={formData.total_amount || ''} onChange={(e) => onFormChange('total_amount', e.target.value)} className="form-control error-total_amount" name="total_amount" />
            )}
          </div>
          <div className="col-12 col-md-6 mb-3 custom-select">
            <Label htmlFor="status" label={t('status')} isRequired />
            {skeleton ? (
              <InputSkeleton />
            ) : (
              <Select
                onChange={(value) => onFormChange('status', value)}
                className="form-control error-status"
                option={{ label: 'label', value: 'value' }}
                defaultValue={{ label: formData.status, value: formData.status }}
                isSearchable={false}
                options={statusTypes}
              />
            )}
          </div>
          <div className="col-12 col-md-6 mb-3 custom-select">
            <Label htmlFor="request_type" label={t('revised')} isRequired />
            {skeleton ? (
              <InputSkeleton />
            ) : (
              <Select
                onChange={(value) => onFormChange('re_request', value)}
                className="form-control error-re_request"
                option={{ label: 'label', value: 'value' }}
                defaultValue={{ label: formData.re_request === 'yes' ? 'Yes' : 'No', value: formData.re_request === 'yes' ? 'yes' : 'no' }}
                isSearchable={false}
                options={[
                  { label: 'Yes', value: 'yes' },
                  { label: 'No', value: 'no' },
                ]}
              />
            )}
          </div>
          <div className="col-12 mb-3">
            <Label htmlFor="request_type" label={t('upload_quotation')} isRequired />
            {skeleton ? (
              <InputSkeleton />
            ) : (
              <div>
                {formData.coverage_details ? (
                  <FilePreviewInput
                    fileName={formData.coverage_details_name}
                    onCancel={() => {
                      setDeletableResource(formData.coverage_details), onFormChange('coverage_details', '');
                    }}
                  />
                ) : (
                  <>
                    {!resource ? (
                      <ImageDragAndDrop fileType="pdf" htmlFor={'document'} selectedImage={(file: File) => setResource(file)} className="form-control error-coverage_details" />
                    ) : (
                      <FilePreviewInput fileName={resource.name} onCancel={() => setResource(null)} />
                    )}
                  </>
                )}
              </div>
            )}
          </div>
          <div className="col-12 col-md-6 mb-3 custom-select">
            <Label htmlFor="uploaded_by" label={t('uploaded_by')} isRequired />
            {skeleton ? (
              <InputSkeleton />
            ) : (
              <AsyncSelect
                onChange={(_value: any, data: any) => {
                  onFormChange('by_user_id', data.id);
                  onFormChange('by_user_name', data.display_name);
                }}
                defaultValue={{
                  id: formData.by_user_id,
                  display_name: formData.by_user_name,
                }}
                className="form-control error-by_user_id"
                option={{ label: 'display_name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllUsers(searchValue, currentPage)}
              />
            )}
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('update')} onClick={onSubmit} width="sm" />
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default EditQuotation;
