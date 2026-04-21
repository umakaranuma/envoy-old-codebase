'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import { AsyncSelect } from '@apptimus-ui/select';
import { Button, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useEffect, useState } from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { fetchAllServiceProviderUsingProductId } from '../../service';
import { toaster } from '@/helpers/services/toaster';
import { createRequest, getQuotationRiskInfoFile } from '../../api-service';

function SelectServiceProvider({
  isOpen,
  onCancel,
  setRequestId,
  formData,
  setFormData,
  afterSave,
  setRiskDocumentData,
}: {
  isOpen: boolean;
  onCancel: Function;
  setRequestId: Function;
  formData: any;
  setFormData: Function;
  afterSave: Function;
  setRiskDocumentData: Function;
}) {
  const t = useTrans('label.quotations,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [opportunityIds, setOpportunityIds] = useState('');
  const [type, setType] = useState('');
  const [leadId, setLeadId] = useState('');
  const [defaultValueInsurer, setDefaultValueInsurer] = useState([]);

  useEffect(() => {
    const opportunity_type_id = formData.opportunity_type_id || [];
    const formatted_str = Array.isArray(opportunity_type_id) ? opportunity_type_id.join(',') : String(opportunity_type_id);
    setOpportunityIds(formatted_str);
    setLeadId(formData.lead_id || '');
    setType(formData.request_type || '');
    async function fetchInsurers() {
      try {
        const result = await fetchAllServiceProviderUsingProductId(formatted_str, leadId);
        const data = Array.isArray(result) ? result : result.data || [];
        const insurers = data.map((item: any) => ({
          id: item.id,
          name: item.name,
        }));
        const allIds = insurers.map((insurer: any) => insurer.id);
        onFormChange('service_provider_id', allIds);
        setDefaultValueInsurer(insurers);
      } catch (error) {
        console.error(error);
      }
    }
    if (formData.opportunity_type_id) {
      fetchInsurers();
    }
  }, [formData.opportunity_type_id, leadId, type]);

  useEffect(() => {
    console.log('formDatasdfsfds', formData);
  }, [formData]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.quotation.store);

    const error: { [key: string]: Array<{ error_type: string; tokens: { _attribute: string } }> } = {};

    if (formData.service_provider_id.length === 0) {
      error['service_provider_id'] = [
        {
          error_type: 'required',
          tokens: {
            _attribute: 'service_provider_id',
          },
        },
      ];
    }

    if (Object.keys(error).length > 0) {
      printError(error, form.quotation.store, tBe);
      return;
    }

    setIsFormProcessing(true);
    try {
      const responseData = await createRequest(formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.quotation.store, tBe);
      }

      if (responseData.is_success) {
        const response = await getQuotationRiskInfoFile(responseData.result.quotation.id);
        if (response.is_success) {
          setRiskDocumentData(response.result);
        }
        handleOpenEmail(responseData.result.quotation.id);
        afterSave(responseData.result.service_providers, responseData.result.quotation.entity_id);
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  const handleOpenEmail = (id: any) => {
    onCancel();
    setTimeout(() => {
      setRequestId(id);
    }, 100);
  };

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('select_insurers')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.quotation.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3 custom-select">
              <Label htmlFor="insurer" label={t('insurer')} isRequired />
              <AsyncSelect
                defaultValue={defaultValueInsurer}
                onChange={(value) => onFormChange('service_provider_id', value)}
                className="form-control error-service_provider_id"
                option={{ label: 'name', value: 'id' }}
                multiple
                loadOptions={() => fetchAllServiceProviderUsingProductId(opportunityIds, leadId)}
              />
            </div>
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

export default SelectServiceProvider;
