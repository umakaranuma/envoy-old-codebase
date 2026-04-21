'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import { AsyncSelect } from '@apptimus-ui/select';
import { Button, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useEffect, useState } from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { fetchAllOpportunities, fetchAllProductsByType } from '@/app/crm/a/sales-management/_utils/services';
import { hexToRgba } from '@/helpers/services/commonService';
import { fetchAllServiceProviderUsingProductId, fetchAllTypesOfOpportunity } from '../../service';
import { toaster } from '@/helpers/services/toaster';
import { createRequest, getQuotationRiskInfoFile } from '../../api-service';
import { getOneOpportunity } from '@/app/crm/a/sales-management/_utils/api-service';
import { InputSkeleton } from '@/components/others/InputSkeleton';

function CreateRequest({ isOpen, onCancel, leadIdFromCRM = '', setSubmissionData }: { isOpen: boolean; onCancel: Function; leadIdFromCRM?: string; setSubmissionData: Function }) {
  const t = useTrans('label.quotations,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({ opportunity_type_id: [], opportunity_types: [], lead_id: '', service_provider_id: [], recipients: [], product_name: '', product_id: '' });
  const [error, setError] = useState('');
  const [skeleton, setSkeleton] = useState(false);
  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  };

  useEffect(() => {
    if (leadIdFromCRM !== '') {
      onFormChange('lead_id', leadIdFromCRM);
      fetchData();
    }
  }, [leadIdFromCRM]);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError('');
    clearError(form.quotation.store);
    setIsFormProcessing(true);
    try {
      const responseData = await createRequest(formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.quotation.store, tBe);
      }

      if (responseData.system_code === 'VALIDATION_ERROR') {
        setError(responseData.message);
      }

      if (responseData.is_success) {
        const response = await getQuotationRiskInfoFile(responseData.result.quotation.id);
        let document;
        if (response.is_success) {
          document = response.result;
          setSubmissionData({ id: responseData.result.quotation.entity_id, data: document, recipients: formData.recipients });
          toaster.success(tBe(responseData.message));
          onCancel();
        } else {
          console.error('An error occurred while fetching the document.');
        }
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  const fetchData = async () => {
    setSkeleton(true);
    const responseData = await getOneOpportunity(leadIdFromCRM);
    if (responseData?.is_success) {
      const data = responseData.result;
      // setData(responseData.result);
      onFormChange('opportunity_type_id', data.risk_types ? data.risk_types?.map((type: any) => type.id) : []);
      onFormChange('opportunity_types', data.risk_types ? data.risk_types : []);
      const productType = data.risk_types.length === 1 ? 'product' : 'group';
      onFormChange('product_type', productType);
      onFormChange('product_id', productType === 'product' ? data.product_id : data.product_group_id);
      onFormChange('product_name', productType === 'product' ? data.product_name : data.product_group_name);
    }
    setSkeleton(false);
  };

  return (
    <Modal isOpen={isOpen} onBackdrop={() => onCancel()}>
      <ModalHeader title={t('add_new_entity', { entity: t('request') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.quotation.store}`}>
        <ModalBody>
          <div className="row">
            {leadIdFromCRM === '' && (
              <div className="col-12 mb-3 custom-select">
                <Label label={t('lead')} isRequired />
                <AsyncSelect
                  onChange={(value, data) => {
                    // onFormChange('opportunity_type_id', []);
                    onFormChange('lead_id', value);
                    onFormChange('opportunity_type_id', data.opportunity_types ? data.opportunity_types?.map((type: any) => type.id) : []);
                    onFormChange('opportunity_types', data.opportunity_types ? data.opportunity_types?.map((type: any) => ({ id: type.id, title: type.name })) : []);
                    const productType = data.opportunity_types.length === 1 ? 'product' : 'group';
                    onFormChange('product_type', productType);
                    onFormChange('product_id', productType === 'product' ? data.product_id : data.product_group_id);
                    onFormChange('product_name', productType === 'product' ? data.product_name : data.product_group_name);
                  }}
                  loadOptions={(searchValue: any, currentPage: any) => fetchAllOpportunities(searchValue, currentPage, 'opportunity_qualified', true)}
                  option={{
                    labelFn: (option) => (
                      <>
                        <div className="text">{option.title}</div>
                        <div className="d-flex align-items-center gap-2 mt-1">
                          <div
                            className={'rounded-5 fw-semibold badge error-lead_id'}
                            style={{ background: hexToRgba(option.stage_color, 0.1), border: `1px solid ${hexToRgba(option.stage_color, 0.4)}`, color: option.stage_color }}
                          >
                            {option.stage_name}
                          </div>
                          <div className="text-muted">|</div>
                          <div className="text">{option.code}</div>
                        </div>
                      </>
                    ),
                    label: 'title',
                    value: 'id',
                  }}
                  className="form-control error-lead_id"
                />
              </div>
            )}
            {formData.lead_id && (
              <>
                <div className="col-12 mb-3 custom-select" key={`risk-${formData.lead_id}-1`}>
                  <Label htmlFor="risk_type" label={t('risk_type')} isRequired />
                  {skeleton ? (
                    <InputSkeleton />
                  ) : (
                    <AsyncSelect
                      onChange={(value) => {
                        onFormChange('opportunity_type_id', value);
                        onFormChange('product_type', '');
                        onFormChange('product_id', '');
                        onFormChange('product_name', '');
                      }}
                      className="form-control error-opportunity_type_id"
                      option={{ label: 'title', value: 'id' }}
                      isSearchable={true}
                      loadOptions={() => fetchAllTypesOfOpportunity(formData.lead_id)}
                      multiple
                      defaultValue={formData.opportunity_types.length > 0 ? formData.opportunity_types : undefined}
                    />
                  )}
                </div>
                <div className="col-12 mb-3 custom-select" key={`product-${formData.opportunity_type_id}`}>
                  <Label htmlFor="product_name" label={t('product')} isRequired />
                  {skeleton ? (
                    <InputSkeleton />
                  ) : (
                    <AsyncSelect
                      onChange={(_value, data) => {
                        onFormChange('product_type', formData.opportunity_type_id.length === 1 ? 'product' : 'group');
                        onFormChange('product_id', data.id);
                        onFormChange('product_name', data.name);
                      }}
                      className="form-control error-product_id"
                      option={{ label: 'name', value: 'id' }}
                      defaultValue={{ name: formData.product_name, id: formData.product_id }}
                      isSearchable={true}
                      loadOptions={(searchValue: any, currentPage: any) => fetchAllProductsByType(searchValue, currentPage, formData.opportunity_type_id.toString())}
                    />
                  )}
                </div>
              </>
            )}
            {/* <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="request_type" label={t('request_type')} isRequired />
              <Select
                onChange={(value) => onFormChange('request_type', value)}
                className="form-control error-request_type"
                option={{ label: 'name', value: 'value' }}
                isSearchable={true}
                options={[
                  { name: 'New', value: 'new' },
                  { name: 'Renew', value: 'renew' },
                ]}
              />
            </div> */}
            {formData.opportunity_type_id.length > 0 && (
              <div className="col-12 mb-3 custom-select" key={`partner-${formData.opportunity_type_id.length}`}>
                <Label htmlFor="insurer" label={t('insurer')} isRequired />
                <AsyncSelect
                  onChange={(value, data) => {
                    onFormChange('service_provider_id', value);
                    onFormChange('recipients', data);
                  }}
                  className="form-control error-service_provider_id"
                  option={{ label: 'name', value: 'id' }}
                  multiple
                  key={formData.opportunity_type_id.length}
                  loadOptions={() => fetchAllServiceProviderUsingProductId(formData.opportunity_type_id.toString(), formData.lead_id)}
                />
              </div>
            )}
            {error && <div className="err-msg">{tBe(error)}</div>}
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('next')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default CreateRequest;
