import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { FormEvent, useEffect, useState } from 'react';
import { initFormData } from '../model';
import { getOneChannel, getOneCurrency, getOneHealth, getOneOpportunity, getOneOpportunityState, updateOpportunity } from '../api-service';
import { useTrans } from '@/helpers/services/lang/langService';
import { AsyncSelect, Select } from '@apptimus-ui/select';
import {
  fetchAllAcountManger,
  fetchAllChannel,
  fetchAllCountries,
  fetchAllCurrency,
  fetchAllOpportunityStages,
  fetchAllOpportunityTypes,
  fetchAllProductsByType,
  fetchAllSalesAgents,
} from '../services';
import { healthCount, opportunityTypes } from '../constants';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { getOneUser } from '../../../tasks/_utils/api-service';

export const SalesManagementsEdit = ({ isOpen, editId, afterUpdate, onCancel }: { isOpen: boolean; editId: string; onCancel: Function; afterUpdate: Function }) => {
  const t = useTrans('label.sales_managements,otr.common,be.msg');

  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);
  const [skeleton, setSkeleton] = useState(true);
  const [defaultStageValue, setDefaultStageValue] = useState({ id: '', name: '' });
  const [defaultChannelValue, setDefaultChannelValue] = useState({ id: '', name: '' });
  const [defaultHealthValue, setDefaultHealthValue] = useState({ label: '', value: '' });
  const [defaultCurrencyIdIdValue, setDefaultCurrencyIdIdValue] = useState({ id: '', name: '' });
  const [defaultAccountManagerIdValue, setDefaultAccountManagerIdValue] = useState({ id: '', name: '' });
  const [defaultCountryValue, setDefaultCountryValue] = useState({ id: '', name: '' });
  const [defaultSalesAgentIdValue, setDefaultSalesAgentIdValue] = useState();
  const tBe = useTrans('be.msg,be.error,be.attri');

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneOpportunity(editId);

      if (responseData?.is_success) {
        const data = responseData.result;
        onFormChange('title', data.title);
        onFormChange('type', data.type);
        onFormChange('remarks', data.remarks);
        onFormChange('lead_value', data.lead_value);
        onFormChange('sale_value', data.sale_value);
        onFormChange('country_name', data.country_name);
        onFormChange('country_id', data.country_id);
        onFormChange('last_contacted_date', data.last_contacted_date);
        onFormChange('opportunity_types', data.risk_types ?? []);
        onFormChange('opportunity_type_id', data.risk_types?.length > 0 ? data.risk_types.map((data: any) => data.id) : []);
        const productType = data.risk_types?.length === 1 ? 'product' : 'group';
        console.log('productType', productType);

        onFormChange('product_type', productType);
        onFormChange('product_id', productType === 'product' ? data.product_id : data.product_group_id);
        onFormChange('product_name', productType === 'product' ? data.product_name : data.product_group_name);

        const stageId = data.stage_id;
        const channelId = data.channel_id;
        const healthId = data.current_health_id;
        const currencyId = data.currency_id;
        const accountManagerId = data.account_manager_id;
        const salesAgentId = data.sales_agent_id;

        setDefaultCountryValue({ id: data.country_id, name: data.country_name });

        if (stageId) {
          onFormChange('stage_id', stageId);
          const response = await getOneOpportunityState(stageId);
          if (response.is_success) {
            setDefaultStageValue(response.result);
          }
        }

        if (channelId) {
          onFormChange('channel_id', channelId);
          const response = await getOneChannel(channelId);
          if (response.is_success) {
            setDefaultChannelValue(response.result);
          }
        }
        if (channelId) {
          onFormChange('channel_id', channelId);
          const response = await getOneChannel(channelId);
          if (response.is_success) {
            setDefaultChannelValue(response.result);
          }
        }

        if (healthId) {
          const response = await getOneHealth(editId, healthId);
          if (response.is_success) {
            const health: any = healthCount.find((obj: any) => obj.value.toString() === response.result.health.toString());
            onFormChange('health', health?.value);
            setDefaultHealthValue(health);
          }
        }

        if (currencyId) {
          onFormChange('currency_id', currencyId);
          const response = await getOneCurrency(currencyId);
          if (response.is_success) {
            setDefaultCurrencyIdIdValue(response.result);
          }
        }

        if (accountManagerId) {
          onFormChange('account_manager_id', accountManagerId);
          const response = await getOneUser(accountManagerId);
          if (response.is_success) {
            setDefaultAccountManagerIdValue(response.result);
          }
        }

        if (salesAgentId) {
          onFormChange('sales_agent_id', salesAgentId);
          const response = await getOneUser(salesAgentId);
          if (response.is_success) {
            setDefaultSalesAgentIdValue(response.result);
          }
        }
      }
      setSkeleton(false);
    };

    if (editId) {
      setSkeleton(true);
      fetchData();
    }
  }, [editId]);

  useEffect(() => {
    console.log('formData', formData);
  }, [formData]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.opportunity_type.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updateOpportunity(editId, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.opportunity_type.update, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        onCancel();
        afterUpdate();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen} size="lg">
      <ModalHeader title={t('edit_entity', { entity: t('leads') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.opportunity_crud.update}`}>
        <ModalBody>
          <div className="row" id={`${form.opportunity_crud.store}`}>
            <div className="row">
              <div className="col-12 col-md-6 mb-3 custom-select">
                <Label htmlFor="type" label={t('type')} isRequired />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <Select
                    onChange={(value) => onFormChange('type', value)}
                    className="form-control error-type"
                    option={{ label: 'label', value: 'value' }}
                    isSearchable={false}
                    options={opportunityTypes}
                    defaultValue={{
                      value: formData.type,
                      label: formData.type,
                    }}
                  />
                )}
              </div>
              <div className="col-12 col-md-6 mb-3">
                <Label label={t('name')} />
                {skeleton ? <InputSkeleton /> : <Input value={formData.title} onChange={(e) => onFormChange('title', e.target.value)} className="error-title" name="title" />}
              </div>
              <div className="col-12 col-md-6 mb-3 custom-select">
                <Label htmlFor="lead_stage" label={t('lead_stage')} isRequired />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <AsyncSelect
                    onChange={(value) => onFormChange('stage_id', value)}
                    className="error-stage_id"
                    loadOptions={fetchAllOpportunityStages}
                    option={{ label: 'name', value: 'id' }}
                    defaultValue={defaultStageValue}
                    isSearchable={true}
                  />
                )}
              </div>
              <div className="col-12 col-md-6 mb-3 custom-select" key={`opportunity-${formData.type}`}>
                <Label label={t('risk_type')} />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <AsyncSelect
                    //onChange={(value) => onFormChange('opportunity_type_id', value)}
                    className="form-control error-opportunity_type_id"
                    option={{ label: 'title', value: 'id' }}
                    isSearchable={true}
                    loadOptions={(searchValue, currentPage) => fetchAllOpportunityTypes(searchValue, currentPage)}
                    multiple={formData.type === 'Corporate' ? true : false}
                    onChange={(_value, data) => {
                      if (formData.type === 'Corporate') {
                        onFormChange('opportunity_types', data || []);
                        onFormChange('opportunity_type_id', data.map((data: any) => data.id) || []);
                      } else {
                        onFormChange('opportunity_types', data || []);
                        onFormChange('opportunity_type_id', data.id ? [data.id] : []);
                      }
                      onFormChange('product_type', '');
                      onFormChange('product_id', '');
                      onFormChange('product_name', '');
                    }}
                    defaultValue={formData?.opportunity_types ? (formData.type === 'Corporate' ? formData.opportunity_types : formData.opportunity_types[0]) : []}
                  />
                )}
              </div>
              {formData.opportunity_type_id.length > 0 && (
                <div className="col-12 col-md-6 mb-3 custom-select" key={`product-${formData.opportunity_type_id}`}>
                  <Label htmlFor="product_name" label={t('product_name')} isRequired />
                  {skeleton ? (
                    <InputSkeleton />
                  ) : (
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
                  )}
                </div>
              )}
              <div className="col-12 col-md-6 mb-3 custom-select">
                <Label htmlFor="channel" label={t('channel')} />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <AsyncSelect
                    onChange={(value) => onFormChange('channel_id', value)}
                    className="error-channel_id"
                    loadOptions={fetchAllChannel}
                    option={{
                      label: 'name',
                      value: 'id',
                    }}
                    defaultValue={defaultChannelValue}
                    isSearchable={true}
                  />
                )}
              </div>
              <div className="col-12 col-md-6 mb-3 custom-select">
                <Label htmlFor="health" label={t('health')} />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <Select
                    onChange={(value) => onFormChange('health', value)}
                    className="form-control error-health"
                    option={{ label: 'label', value: 'value' }}
                    isSearchable={false}
                    options={healthCount}
                    defaultValue={defaultHealthValue}
                  />
                )}
              </div>
              <div className="col-12 col-md-6 mb-3 custom-select">
                <Label htmlFor="currency" label={t('currency')} isRequired />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <AsyncSelect
                    onChange={(value) => onFormChange('currency_id', value)}
                    className="error-currency_id"
                    loadOptions={fetchAllCurrency}
                    option={{ label: 'symbol', value: 'id' }}
                    defaultValue={defaultCurrencyIdIdValue}
                    isSearchable={true}
                  />
                )}
              </div>
              <div className="col-12 col-md-6 mb-3">
                <Label label={t('last_contact_date')} />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <Input
                    value={formData.last_contacted_date || ''}
                    onChange={(e) => onFormChange('last_contacted_date', e.target.value)}
                    className="form-control error-last_contacted_date"
                    id="last_contacted_date"
                    name="last_contacted_date"
                    type="date"
                  />
                )}
              </div>
              <div className="col-12 col-md-6 mb-3 custom-select">
                <Label htmlFor="account_manager" label={t('account_manager')} />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <AsyncSelect
                    onChange={(value) => onFormChange('account_manager_id', value)}
                    className="error-account_manager_id"
                    loadOptions={fetchAllAcountManger}
                    option={{ label: 'display_name', value: 'id' }}
                    defaultValue={defaultAccountManagerIdValue}
                    isSearchable={true}
                  />
                )}
              </div>
              <div className="col-12 col-md-6 mb-3 custom-select">
                <Label htmlFor="sales_agent" label={t('sales_agent')} />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <AsyncSelect
                    onChange={(value) => onFormChange('sales_agent_id', value)}
                    className="error-sales_agent_id"
                    loadOptions={fetchAllSalesAgents}
                    option={{ label: 'display_name', value: 'id' }}
                    defaultValue={defaultSalesAgentIdValue}
                    isSearchable={true}
                  />
                )}
              </div>
              <div className="col-12 col-md-6 mb-3">
                <Label label={t('lead_value')} />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <Input
                    value={formData.lead_value || ''}
                    onChange={(e) => onFormChange('lead_value', e.target.value)}
                    className="form-control error-lead_value"
                    id="lead_value"
                    name="lead_value"
                    type="number"
                  />
                )}
              </div>
              <div className="col-12 col-md-6 mb-3">
                <Label label={t('sale_value')} />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <Input
                    value={formData.sale_value || ''}
                    onChange={(e) => onFormChange('sale_value', e.target.value)}
                    className="form-control error-sale_value"
                    id="sale_value"
                    name="sale_value"
                    type="number"
                  />
                )}
              </div>
              <div className="col-12 col-md-6 mb-3 custom-select">
                <Label htmlFor="country" label={t('country')} />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <AsyncSelect
                    onChange={(value) => onFormChange('country_id', value)}
                    className="form-control error-country"
                    option={{ label: 'name', value: 'id' }}
                    isSearchable={true}
                    defaultValue={defaultCountryValue}
                    loadOptions={(searchValue, currentPage) => fetchAllCountries(searchValue, currentPage)}
                  />
                )}
              </div>
              <div className="col-12 mb-3">
                <Label htmlFor="remarks" label={t('remarks')} />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <Input type="textarea" value={formData.remarks || ''} onChange={(e) => onFormChange('remarks', e.target.value)} className="form-control error-remarks" name="remarks" />
                )}
              </div>
            </div>
            {/* <div>
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
            </div> */}
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('update')} type="submit" width="sm" isLoading={isFormProcessing} disabled={skeleton} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
};
