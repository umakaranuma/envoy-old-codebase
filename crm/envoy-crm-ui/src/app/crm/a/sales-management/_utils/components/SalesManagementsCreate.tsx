import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { useEffect, useMemo, useState } from 'react';
import { initFormData } from '../model';
import { toaster } from '@/helpers/services/toaster';
import { createOpportunity, getOneCountry, getOneCurrency, getOpportunityStages } from '../api-service';
import { useTrans } from '@/helpers/services/lang/langService';
import { AsyncSelect, Select } from '@apptimus-ui/select';
import {
  fetchAllChannel,
  fetchAllContacts,
  fetchAllCountries,
  fetchAllCurrency,
  fetchAllCustomers,
  fetchAllIssuedPolicies,
  fetchAllOpportunityStages,
  fetchAllOpportunityTypes,
  fetchAllProductsByType,
  fetchAllSalesAgents,
} from '../services';
import { Dropdown, DropdownItem } from '@apptimus-ui/dropdown';
import { Flexicon } from '@apptimus-ui/flexicon';
import PhoneInput from 'react-phone-input-2';
import 'react-phone-input-2/lib/style.css';
import { opportunityTypes } from '../constants';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { getLocalStorage } from '@/helpers/handlers/localStorageHandler';
import { local_storage } from '@/constans/StorageKeys';
import { getSetting } from '@/api-services/common';
import PolicyCard from '@/components/others/page-related/PolicyCard';

function SalesManagementsCreate({ isOpen, onCancel, afterSave, defaultStageId }: { isOpen: boolean; onCancel: Function; afterSave: Function; defaultStageId: string | null }) {
  const tBe = useTrans('be.msg,be.error,be.attri');
  const t = useTrans('label.sales_managements,otr.common,be.msg');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);
  const [isSameLeadStage, setIsSameLeadStage] = useState(false);
  const [stageDefaultValue, setstageDefaultValue] = useState({ id: 0, name: '' });
  // const [currencyDefaultValue, setCurrencyDefaultValue] = useState({ id: 0, name: '' });
  const getSalesAgent = useMemo(() => getLocalStorage(local_storage.auth_user_info), []);

  useEffect(() => {
    if (getSalesAgent) {
      onFormChange('sales_agent_id', getSalesAgent?.id);
      onFormChange('salse_agent_name', getSalesAgent?.display_name);
    }
  }, []);

  useEffect(() => {
    onFormChange('stage_id', defaultStageId?.toString());
  }, [defaultStageId]);

  useEffect(() => {
    const fetch = async () => {
      const responseData = await getOpportunityStages({ limit: '100' });

      if (responseData.is_success) {
        const obj = responseData.result.find((obj: any) => obj.type === 'LEAD');
        onFormChange('stage_id', obj.id);
        setstageDefaultValue(obj);
      }
    };

    if (defaultStageId === null) {
      fetch();
    }
  }, []);

  useEffect(() => {
    fetchBaseCountry();
    fetchBaseCurrency();
  }, []);

  const fetchBaseCountry = async () => {
    const response = await getSetting('BASE_COUNTRY');
    if (response.is_success) {
      const BASE_COUNTRY_ID = response?.result?.value || '';
      if (BASE_COUNTRY_ID) {
        const responseData = await getOneCountry(BASE_COUNTRY_ID);
        if (responseData.is_success) {
          onFormChange('country_id', responseData.result.id);
          onFormChange('country_name', responseData.result.name);
          // setCurrencyDefaultValue(responseData.result);
        }
      }
    }
  };

  const fetchBaseCurrency = async () => {
    const response = await getSetting('BASE_CURRENCY');
    if (response.is_success) {
      const BASE_CURRENCY_ID = response?.result?.value || '';
      if (BASE_CURRENCY_ID) {
        const responseData = await getOneCurrency(BASE_CURRENCY_ID);
        if (responseData.is_success) {
          onFormChange('currency_id', responseData.result.id);
          onFormChange('currency_code', responseData.result.code);
          // setCurrencyDefaultValue(responseData.result);
        }
      }
    }
  };

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  useEffect(() => {
    setIsSameLeadStage(false);
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
        afterSave(responseData.result.id);
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }
  console.log('defaultStageId', defaultStageId);

  return (
    <Modal isOpen={isOpen} size="xl">
      <ModalHeader title={t('create_new_entity', { entity: t('leads_details') })} onClose={() => onCancel()} />
      <ModalBody>
        <div className="row" id={`${form.opportunity_crud.store}`}>
          <div className="row col-8">
            {/* <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('request_type')} isRequired />
              <Select
                onChange={(_value, data) => {
                  onFormChange('transaction_type', data.value);
                  onFormChange('request_type_label', data.label);
                }}
                className="form-control error-request_type"
                option={{ label: 'label', value: 'value' }}
                isSearchable={false}
                defaultValue={{ label: formData.request_type_label, value: formData.transaction_type }}
                options={[
                  { label: 'New', value: 'new' },
                  { label: 'Renewal', value: 'renewal' },
                ]}
              />
            </div> */}
            <div className="col-12 d-flex align-items-center gap-4 mb-3">
              <div className="d-flex align-items-center gap-1">
                <Input
                  type="radio"
                  id="new-type"
                  name="transaction_type"
                  value="new"
                  className="mb-2"
                  checked={formData.transaction_type === 'new'}
                  onChange={() => {
                    onFormChange('transaction_type', 'new');
                    onFormChange('contact_info_type', 'manual');
                    onFormChange('issued_policy_id', null);
                    onFormChange('customer_id', null);
                    onFormChange('customer_name', '');
                    onFormChange('opportunity_types', []);
                    onFormChange('opportunity_type_id', []);
                    onFormChange('type', 'Personal');
                  }}
                />
                <Label htmlFor="new-type" label={t('new')} />
              </div>
              <div className="d-flex align-items-center gap-1">
                <Input
                  type="radio"
                  id="renewal-type"
                  name="transaction_type"
                  checked={formData.transaction_type === 'renewal'}
                  onChange={() => {
                    onFormChange('transaction_type', 'renewal'), onFormChange('contact_info_type', 'customer');
                  }}
                  value="renewal"
                  className="mb-2"
                />
                <Label htmlFor="renewal-type" label={t('renewal')} />
              </div>
            </div>
            {/* {formData.transaction_type === 'renewal' && (
              <div className="col-12 col-md-6 mb-3 custom-select">
                <Label label={t('select_lead')} isRequired />
                <AsyncSelect
                  onChange={(_value, data) => {
                    onFormChange('opportunity_id', data.id);
                    onFormChange('type', data.type ? data.type : '');
                    onFormChange('title', data.title ? data.title : '');
                    onFormChange('stage_name', data.stage_name ? data.stage_name : '');
                    onFormChange('stage_id', data.stage_id ? data.stage_id : null);
                    onFormChange('channel_id', data.channel_id ? data.channel_id : null);
                    onFormChange('channel_name', data.channel_name ? data.channel_name : '');
                    onFormChange('current_health', data.current_health ? data.current_health : '');
                    onFormChange('current_health_id', data.current_health_id ? data.current_health_id : null);
                    onFormChange('currency_symbol', data.currency_symbol ? data.currency_symbol : '');
                    onFormChange('currency_id', data.currency_id ? data.currency_id : null);
                    onFormChange('last_contacted_date', data.last_contacted_date ? data.last_contacted_date : null);
                    onFormChange('salse_agent_name', data.salse_agent_name ? data.salse_agent_name : '');
                    onFormChange('sales_agent_id', data.sales_agent_id ? data.sales_agent_id : null);
                    onFormChange('remarks', data.remarks ? data.remarks : '');
                    onFormChange('email', data.email ? data.email : '');
                    onFormChange('contact_number', data.contact_number ? data.contact_number : '');
                    onFormChange('account_manager_name', data.account_manager_name ? data.account_manager_name : '');
                    onFormChange('account_manager_id', data.account_manager_id ? data.account_manager_id : null);
                    onFormChange('opportunity_types', data.opportunity_types ? data.opportunity_types.map((op: any) => ({ title: op.name, id: op.id })) : []);
                    onFormChange('opportunity_type_id', data.opportunity_types ? data.opportunity_types.map((op: any) => op.id) : []);
                    onFormChange('contact_id', data.contact_id ? data.contact_id : null);
                    onFormChange('contact_name', data.contact?.name ? data.contact.name : '');
                    onFormChange('customer_id', data.customer_id ? data.customer_id : null);
                    onFormChange('customer_name', data.customer?.name ? data.customer.name : '');
                  }}
                  className="form-control error-selected_lead"
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
                  isSearchable={true}
                  loadOptions={(searchValue: any, currentPage: any) => fetchAllOpportunities(searchValue, currentPage)}
                />
              </div>
            )} */}
            {formData.transaction_type === 'renewal' && (
              <div className="col-12 col-md-6 mb-3 custom-select custom-values">
                <Label label={t('select_policy')} isRequired />
                <AsyncSelect
                  onChange={(_value, data) => {
                    onFormChange('issued_policy_id', data.id);
                    onFormChange('customer_id', data.customer_id);
                    onFormChange('customer_name', data.customer_name);
                    onFormChange('opportunity_types', data.risk_types ? data.risk_types.map((op: any) => ({ title: op.risk_type_name, id: op.risk_type_id })) : []);
                    onFormChange('opportunity_type_id', data.risk_types ? data.risk_types.map((op: any) => op.risk_type_id) : []);
                    onFormChange('type', data.customer_type);
                  }}
                  className="form-control error-issued_policy_id custom-container"
                  // option={{ label: 'brokerage_policy_id', value: 'id' }}
                  isSearchable={true}
                  option={{
                    labelFn: (option) => (
                      <PolicyCard
                        premiumAmount={option.premium_amount}
                        status={option.status}
                        startDate={option.start_date}
                        endDate={option.end_date}
                        policyNumber={option.brokerage_policy_id}
                        productName={option.product}
                      />
                    ),
                    label: 'brokerage_policy_id',
                    value: 'id',
                  }}
                  loadOptions={(searchValue: any, currentPage: any) => fetchAllIssuedPolicies(searchValue, currentPage)}
                />
              </div>
            )}
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="type" label={t('type')} isRequired />
              {formData.transaction_type === 'renewal' ? (
                <Input disabled value={formData.type} />
              ) : (
                <Select
                  onChange={(value) => {
                    onFormChange('opportunity_types', []);
                    onFormChange('opportunity_type_id', []);
                    onFormChange('type', value);
                  }}
                  className="form-control error-type"
                  option={{ label: 'label', value: 'value' }}
                  isSearchable={false}
                  options={opportunityTypes}
                  defaultValue={formData.type && { label: formData.type, value: formData.type }}
                />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input label={t('name')} value={formData.title || ''} onChange={(e) => onFormChange('title', e.target.value)} className="form-control error-title" name="title" />
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
            <div className="col-12 col-md-6 mb-3 custom-select" key={`opportunity-${formData.type}`}>
              <Label label={t('risk_type')} />
              <AsyncSelect
                //onChange={(value) => onFormChange('opportunity_type_id', value)}
                className="form-control error-opportunity_type_id"
                option={{ label: 'title', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllOpportunityTypes(searchValue, currentPage)}
                multiple={formData.type === 'Corporate' ? true : false}
                onChange={(_value, data) => {
                  console.log('data', data);

                  if (formData.type === 'Corporate') {
                    onFormChange('opportunity_types', data || []);
                    onFormChange('opportunity_type_id', data.map((data: any) => data.id) || []);
                  } else {
                    onFormChange('opportunity_types', data || []);
                    onFormChange('opportunity_type_id', data.id ? [data.id] : []);
                  }
                }}
                defaultValue={formData?.opportunity_types ? (formData.type === 'Corporate' ? formData.opportunity_types : formData.opportunity_types[0]) : []}
              />
            </div>
            {formData.opportunity_type_id.length > 0 && (
              <div className="col-12 col-md-6 mb-3 custom-select" key={`product-${formData.opportunity_type_id.toString()}`}>
                <Label htmlFor="product_name" label={t('product_name')} isRequired />
                <AsyncSelect
                  onChange={(_value, data) => {
                    onFormChange('product_type', formData.opportunity_type_id.length === 1 ? 'product' : 'group');
                    onFormChange('product_id', data.id), onFormChange('product_name', data.name);
                    onFormChange('insurer_id', ''), onFormChange('insurer_name', '');
                  }}
                  className="form-control error-product_id"
                  option={{ label: 'name', value: 'id' }}
                  defaultValue={{ name: formData.product_name, id: formData.product_id }}
                  isSearchable={true}
                  loadOptions={(searchValue: any, currentPage: any) => fetchAllProductsByType(searchValue, currentPage, formData.opportunity_type_id.toString())}
                />
              </div>
            )}
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="channel" label={t('channel')} />
              <AsyncSelect
                onChange={(_value, data) => {
                  onFormChange('channel_id', data.id);
                  onFormChange('channel_name', data.name);
                }}
                className="form-control error-channel_id"
                option={{
                  label: 'name',
                  value: 'id',
                }}
                defaultValue={{ id: formData.channel_id, name: formData.channel_name }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllChannel(searchValue, currentPage)}
              />
            </div>
            {/* <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="health" label={t('health')} />
              <Select
                onChange={(_value, data) => {
                  onFormChange('current_health', data.value);
                  onFormChange('current_health_id', data.value);
                }}
                className="form-control error-health"
                option={{ label: 'label', value: 'value' }}
                isSearchable={false}
                options={healthCount}
                defaultValue={{ label: formData.current_health, value: formData.h }}
              />
            </div> */}
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="currency" label={t('currency')} isRequired />
              <AsyncSelect
                onChange={(_value, data) => {
                  onFormChange('currency_id', data.id);
                  onFormChange('currency_code', data.code);
                }}
                className="form-control error-currency_id"
                option={{ label: 'code', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllCurrency(searchValue, currentPage)}
                defaultValue={{ id: formData.currency_id, code: formData.currency_code }}
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                label={t('last_contact_date')}
                type="date"
                value={formData.last_contacted_date}
                onChange={(e) => onFormChange('last_contacted_date', e.target.value)}
                className="form-control error-last_contacted_date"
                name="last_contacted_date"
              />
            </div>
            {/* <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('account_manager')} />
              <AsyncSelect
                onChange={(_value, data) => {
                  onFormChange('account_manager_id', data.id);
                  onFormChange('account_manager_name', data.display_name);
                }}
                className="form-control error-account_manager_id"
                option={{ label: 'display_name', value: 'id' }}
                isSearchable={true}
                defaultValue={{ id: formData.account_manager_id, display_name: formData.account_manager_name }}
                loadOptions={(searchValue, currentPage) => fetchAllAcountManger(searchValue, currentPage)}
              />
            </div> */}
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('sales_agent')} />
              <AsyncSelect
                onChange={(_value, data) => {
                  onFormChange('sales_agent_id', data.id);
                  onFormChange('salse_agent_name', data.display_name);
                }}
                className="form-control error-sales_agent_id"
                option={{ label: 'display_name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllSalesAgents(searchValue, currentPage)}
                defaultValue={formData.sales_agent_id ? { id: formData.sales_agent_id, display_name: formData.salse_agent_name } : undefined}
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                label={t('lead_value')}
                type="number"
                value={formData.lead_value || ''}
                onChange={(e) => onFormChange('lead_value', e.target.value)}
                className="form-control error-lead_value"
                name="lead_value"
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                label={t('sale_value')}
                type="number"
                value={formData.sale_value || ''}
                onChange={(e) => onFormChange('sale_value', e.target.value)}
                className="form-control error-sale_value"
                name="sale_value"
              />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="country" label={t('country')} />
              <AsyncSelect
                onChange={(value, data) => {
                  onFormChange('country_id', value);
                  onFormChange('country_name', data.name);
                }}
                className="form-control error-country"
                option={{ label: 'name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllCountries(searchValue, currentPage)}
                defaultValue={formData.country_id ? { name: formData.country_name, id: formData.country_id } : undefined}
              />
            </div>
            <div className="col-12 col-md-6 mb-3  mb-3">
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
          <div className="col-4" key={formData.opportunity_id}>
            <div className="d-flex flex-row align-items-center mb-2">
              <div className="fw-medium me-2">{t('contact_info')}</div>
              {!isSameLeadStage && formData.transaction_type !== 'renewal' && (
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
                  key={formData.transaction_type}
                  onChange={(_value, data) => {
                    onFormChange('customer_id', data.id);
                    onFormChange('customer_name', data.name);
                  }}
                  className="form-control error-customer_id"
                  option={{ label: 'name', value: 'id' }}
                  isSearchable={true}
                  defaultValue={{ id: formData.customer_id, name: formData.customer_name }}
                  loadOptions={(searchValue, currentPage) => fetchAllCustomers(searchValue, currentPage, formData.type.toLowerCase())}
                />
              </div>
            )}
            {formData.contact_info_type === 'contact' && (
              <div className="col-12 mb-3 custom-select">
                <Label htmlFor="contacts" label={t('contacts')} isRequired />
                <AsyncSelect
                  onChange={(_value, data) => {
                    onFormChange('contact_id', data.id);
                    onFormChange('contact_name', data.name);
                  }}
                  className="form-control error-contact_id"
                  option={{ label: 'name', value: 'id' }}
                  isSearchable={true}
                  defaultValue={{ id: formData.contact_id, name: formData.contact_name }}
                  loadOptions={(searchValue, currentPage) => fetchAllContacts(searchValue, currentPage)}
                />
              </div>
            )}
            {formData.contact_info_type === 'manual' && (
              <>
                <div className="col-12 mb-3">
                  <Input label={t('email')} value={formData.email || ''} onChange={(e) => onFormChange('email', e.target.value)} className="form-control error-email" name="email" />
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
