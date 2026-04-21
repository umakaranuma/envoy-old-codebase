import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { useEffect, useMemo, useState } from 'react';
import { initFormData, IOpportunity } from './model';
import { toaster } from '@/helpers/services/toaster';
import { createOpportunity, getOneCurrency, getOpportunityStages } from './api-service';
import { useTrans } from '@/helpers/services/lang/langService';
import { AsyncSelect, Select } from '@apptimus-ui/select';
import { fetchAllAcountManger, fetchAllChannel, fetchAllContacts, fetchAllCurrency, fetchAllCustomers, fetchAllOpportunityStages, fetchAllOpportunityTypes, fetchAllSalesAgents } from './services';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import PhoneInput from 'react-phone-input-2';
import 'react-phone-input-2/lib/style.css';
import { healthCount, opportunityTypes } from './constants';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';
import { getSetting } from '@/api-services/common';

function SalesManagementsCreate({
  isOpen,
  onCancel,
  afterSave,
  settingId,
  defaultStageId,
}: {
  isOpen: boolean;
  onCancel: Function;
  afterSave: Function;
  settingId: string;
  defaultStageId: string | null;
}) {
  const tBe = useTrans('be.msg,be.error,be.attri');
  const t = useTrans('label.sales_managements,otr.common,be.msg');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState<IOpportunity>(initFormData);
  const [isSameLeadStage, setIsSameLeadStage] = useState(false);
  const [stageDefaultValue, setstageDefaultValue] = useState({ id: 0, name: '' });
  const [currencyDefaultValue, setCurrencyDefaultValue] = useState({ id: 0, name: '' });
  const getSalesAgent = useMemo(() => getLocalStorage(local_storage.auth_user_info), []);

  useEffect(() => {
    if (getSalesAgent) {
      onFormChange('sales_agent_id', getSalesAgent.id);
    }
  }, [getSalesAgent]);

  useEffect(() => {
    onFormChange('stage_id', defaultStageId?.toString());
  }, [defaultStageId]);

  const typeDefaultValue = useMemo(() => {
    return opportunityTypes.find((obj) => obj.value === 'Personal');
  }, []);

  useEffect(() => {
    const fectch = async () => {
      const responseData = await getOpportunityStages({ limit: '100' });

      if (responseData.is_success) {
        const obj = responseData.result.find((obj: any) => obj.type === 'LEAD');
        onFormChange('stage_id', obj.id);
        setstageDefaultValue(obj);
      }
    };

    if (defaultStageId === null) {
      fectch();
    }
  }, []);

  useEffect(() => {
    const fectch = async () => {
      const response = await getSetting('BASE_CURRENCY');
      if (response.is_success) {
        const BASE_CURRENCY_ID = response?.result?.value || '';
        if (BASE_CURRENCY_ID) {
          const responseData = await getOneCurrency(BASE_CURRENCY_ID);
          if (responseData.is_success) {
            onFormChange('currency_id', responseData.result.id);
            setCurrencyDefaultValue(responseData.result);
          }
        }
      }
    };
    fectch();
  }, []);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  useEffect(() => {
    if (settingId === formData.stage_id?.toString()) {
      setIsSameLeadStage(true);
      onFormChange('contact_info_type', 'customer');
    } else {
      setIsSameLeadStage(false);
    }
  }, [formData.stage_id]);

  async function onSubmit() {
    clearError(form.opportunity_crud.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createOpportunity(formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.opportunity_crud.store, tBe);
      }

      if (responseData.is_success) {
        onCancel();
        afterSave();
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen} size="xl">
      <ModalHeader title={t('create_new_entity', { entity: t('leads_details') })} onClose={() => onCancel()} />
      <ModalBody>
        <div className="row" id={`${form.opportunity_crud.store}`}>
          <div className="row col-8">
            <div className="col-12 col-md-6 mb-3">
              <Input label={t('name')} value={formData.title || ''} onChange={(e) => onFormChange('title', e.target.value)} className="form-control error-title" name="title" />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="type" label={t('type')} isRequired />
              <Select
                onChange={(value) => onFormChange('type', value)}
                className="form-control error-type"
                option={{ label: 'label', value: 'value' }}
                isSearchable={false}
                options={opportunityTypes}
                defaultValue={typeDefaultValue}
              />
            </div>
            {defaultStageId === null && (
              <div className="col-12 col-md-6 mb-3 custom-select">
                <Label htmlFor="lead_stage" label={t('lead_stage')} isRequired />
                <AsyncSelect
                  onChange={(value) => onFormChange('stage_id', value)}
                  className="form-control error-stage_id"
                  option={{ label: 'name', value: 'id' }}
                  isSearchable={true}
                  loadOptions={(searchValue, currentPage) => fetchAllOpportunityStages(searchValue, currentPage, 'WON,LOSS')}
                  defaultValue={stageDefaultValue}
                />
              </div>
            )}
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="channel" label={t('channel')} />
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
              <Label htmlFor="channel" label={t('product_category')} />
              <AsyncSelect
                onChange={(value) => onFormChange('opportunity_type_id', value)}
                className="form-control error-opportunity_type_id"
                option={{ label: 'title', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllOpportunityTypes(searchValue, currentPage)}
                multiple
              />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="health" label={t('health')} />
              <Select
                onChange={(value) => onFormChange('health', value)}
                className="form-control error-health"
                option={{ label: 'label', value: 'value' }}
                isSearchable={false}
                options={healthCount}
              />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="currency" label={t('currency')} isRequired />
              <AsyncSelect
                onChange={(value) => onFormChange('currency_id', value)}
                className="form-control error-currency_id"
                option={{ label: 'symbol', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllCurrency(searchValue, currentPage)}
                defaultValue={currencyDefaultValue}
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                label={t('last_contact_date')}
                type="date"
                value={formData.last_contacted_date || ''}
                onChange={(e) => onFormChange('last_contacted_date', e.target.value)}
                className="form-control error-last_contacted_date"
                name="last_contacted_date"
              />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="currency" label={t('account_manager')} />
              <AsyncSelect
                onChange={(value) => onFormChange('account_manager_id', value)}
                className="form-control error-account_manager_id"
                option={{ label: 'display_name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllAcountManger(searchValue, currentPage)}
              />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="currency" label={t('sales_agent')} />
              <AsyncSelect
                onChange={(value) => onFormChange('sales_agent_id', value)}
                className="form-control error-sales_agent_id"
                option={{ label: 'display_name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllSalesAgents(searchValue, currentPage)}
                defaultValue={getSalesAgent}
              />
            </div>
            <div className="col-12 mb-3">
              <Input
                label={t('remarks')}
                type="textarea"
                value={formData.remarks || ''}
                onChange={(e) => onFormChange('remarks', e.target.value)}
                className="form-control error-remarks"
                name="remarks"
              />
            </div>
          </div>
          <div className="col-4">
            <div className="d-flex flex-row align-items-center mb-2">
              <div className="fw-medium me-2">{t('contact_info')}</div>
              {!isSameLeadStage && (
                <>
                  <div className="mx-2">
                    {' '}
                    {formData.contact_info_type === 'manual' ? (
                      t('select_manually')
                    ) : (
                      <>
                        {t('select_from')} {t(`${formData.contact_info_type}`)}
                      </>
                    )}
                  </div>
                  <Dropdown
                    trigger={
                      <span className="action-icon">
                        <Flexicon icon="chevron-down" variant="line" size={17} />
                      </span>
                    }
                  >
                    {(onClose: Function) => (
                      <>
                        <DropdownItem onClick={() => (onFormChange('contact_info_type', 'customer'), onClose())}>
                          <span>{t('account')}</span>
                        </DropdownItem>
                        <DropdownItem onClick={() => (onFormChange('contact_info_type', 'contact'), onClose())}>
                          <span>{t('contacts')}</span>
                        </DropdownItem>
                        <DropdownItem onClick={() => (onFormChange('contact_info_type', 'manual'), onClose())}>
                          <span>{t('manual')}</span>
                        </DropdownItem>
                      </>
                    )}
                  </Dropdown>
                </>
              )}
            </div>
            {formData.contact_info_type === 'customer' && (
              <div className="col-12 mb-3 custom-select">
                <Label htmlFor="account" label={t('account')} isRequired />
                <AsyncSelect
                  onChange={(value) => onFormChange('customer_id', value)}
                  className="form-control error-customer_id"
                  option={{ label: 'name', value: 'id' }}
                  isSearchable={true}
                  loadOptions={(searchValue, currentPage) => fetchAllCustomers(searchValue, currentPage)}
                />
              </div>
            )}
            {formData.contact_info_type === 'contact' && (
              <div className="col-12 mb-3 custom-select">
                <Label htmlFor="contacts" label={t('contacts')} isRequired />
                <AsyncSelect
                  onChange={(value) => onFormChange('contact_id', value)}
                  className="form-control error-contact_id"
                  option={{ label: 'name', value: 'id' }}
                  isSearchable={true}
                  loadOptions={(searchValue, currentPage) => fetchAllContacts(searchValue, currentPage)}
                />
              </div>
            )}
            {formData.contact_info_type === 'manual' && (
              <>
                <div className="col-12 mb-3">
                  <Input label={t('email')} value={formData.email || ''} onChange={(e) => onFormChange('email', e.target.value)} className="form-control error-email" name="email" isRequired />
                </div>
                <div className="col-12 mb-3">
                  <Label label={t('contact_number')} isRequired />
                  <PhoneInput
                    country={'lk'}
                    enableAreaCodes={true}
                    value={formData.contact_number}
                    inputStyle={{ height: '40px', width: '100%' }}
                    containerStyle={{ height: '40px', width: '100%' }}
                    onChange={(phone) => onFormChange('contact_number', phone)}
                    inputClass="form-control error-contact_number"
                    countryCodeEditable={false}
                  />
                </div>
              </>
            )}
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('create_leads')} width="sm" isLoading={isFormProcessing} onClick={onSubmit} />
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default SalesManagementsCreate;
