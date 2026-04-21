import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { toaster } from '@/helpers/services/toaster';
import { initInsurerProdut } from '../../modal';
import { createInsurerProducts } from '../../api-service';
import { AsyncSelect, Select } from '@apptimus-ui/select';
import { fetchCurrencies, fetchInsurers, fetchOpportunityTypes } from '../../services';
import { fileUploader } from '@/constans/storageService';
import InputFileUploader from '@/components/others/page-related/uploader/InputFileUploader';
import FilePreviewInput from '@/components/others/page-related/uploader/FilePreviewInput';

function CreatInsurerProduct({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const t = useTrans('label.products,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initInsurerProdut);
  const [resource, setResource] = useState<{ document_name: string; document_url: string; file: File } | null>(null);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  const handleFileUpload = async (file: File) => {
    const formData = new FormData();
    if (!file) {
      return null;
    }
    formData.append('file', file);
    const fileName = file.name;
    const fileExtension = file.name.split('.').pop();
    const key = await fileUploader(formData, 'envoy-test');
    return { doc: key, name: fileName, type: fileExtension };
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.product.store);
    setIsFormProcessing(true);

    try {
      const policyFileData = resource ? await handleFileUpload(resource.file) : null;
      const apiFormData = { ...formData, docs: policyFileData?.doc, doc_type: policyFileData?.type, doc_name: policyFileData?.name };
      const responseData = await createInsurerProducts(apiFormData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.product.store, tBe);
      }

      if (responseData.is_success) {
        afterSave(responseData.result.id);
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen} onBackdrop={() => onCancel()} size="xl">
      <ModalHeader title={t('add_new_insurer_product')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.product.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('product_name')} isRequired />
              <Input type="text" name="name" value={formData?.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" placeholder={t('product_name')} />
            </div>
            <div className="col-12 col-md-6 mb-3  custom-select">
              <Label label={t('risk_type')} isRequired />
              <AsyncSelect
                onChange={(_, data) => {
                  onFormChange('category_id', data.id);
                  onFormChange('type', data.title);
                }}
                className="form-control error-category_id"
                option={{ label: 'title', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchOpportunityTypes(searchValue, currentPage)}
              />
            </div>

            <div className="col-12 col-md-6 mb-3  custom-select">
              <Label label={t('insurer_info')} isRequired />
              <AsyncSelect
                onChange={(_, data) => {
                  onFormChange('vendor_id', data.id);
                  onFormChange('insurer', data.name);
                }}
                className="form-control error-vendor_id"
                option={{ label: 'name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchInsurers(searchValue, currentPage)}
              />
            </div>

            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('coverage_level')} isRequired />
              <Select
                onChange={(value) => onFormChange('coverage_level', value)}
                className="form-control error-coverage_level"
                option={{ label: 'name', value: 'id' }}
                isSearchable={false}
                options={[
                  {
                    id: 'Basic',
                    name: 'Basic',
                  },
                  {
                    id: 'Plus',
                    name: 'Plus',
                  },
                  {
                    id: 'Premium',
                    name: 'Premium',
                  },
                ]}
              />
            </div>

            <div className="col-12 col-md-6 mb-3">
              <Label label={t('description')} isRequired />
              <Input
                type="textarea"
                name="description"
                value={formData?.description}
                onChange={(e) => onFormChange('description', e.target.value)}
                placeholder={t('description')}
                className="form-control error-description"
                rows={3}
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('remarks')} />
              <Input
                type="textarea"
                name="remarks"
                value={formData?.remarks}
                onChange={(e) => onFormChange('remarks', e.target.value)}
                placeholder={t('remarks')}
                className="form-control error-remarks"
                rows={3}
              />
            </div>
            <div className="col-12 col-md-6 mb-3  custom-select">
              <Label label={t('currency')} isRequired />
              <AsyncSelect
                onChange={(_, data) => {
                  onFormChange('currency_id', data.id);
                  onFormChange('currency', data.name);
                }}
                className="form-control error-currency_id"
                option={{ label: 'name', value: 'id' }}
                isSearchable={true}
                loadOptions={fetchCurrencies}
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('last_update_date')} isRequired />
              <Input type="date" name="date" value={formData?.date} onChange={(e) => onFormChange('date', e.target.value)} placeholder={t('last_update_date')} className="form-control error-date" />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('terms_conditions')} />
              {resource ? (
                <FilePreviewInput
                  fileName={resource.document_name}
                  onCancel={() => {
                    setResource(null);
                    onFormChange('doc_name', '');
                  }}
                />
              ) : (
                <InputFileUploader
                  data={(file: File) => setResource({ document_name: file.name, document_url: '', file: file })}
                  className="form-control error-invoice_document"
                  name="invoice_document"
                />
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

export default CreatInsurerProduct;
