import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useEffect, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { createContact, createCustomerContacts, createCustomers, createHierarchies } from '../../api-service';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { AsyncSelect, Select } from '@apptimus-ui/select';
import PhoneInput from 'react-phone-input-2';
import 'react-phone-input-2/lib/style.css';
import { initContactFormData, initFormData } from '../../model';
import { FlexField, useFlexField } from '@/components/others/FlexFiled';
import { fetchAllCustomers, fetchContacts } from '../../service';

function AccountsCreate({ isOpen, onCancel, afterSave, parent_id = null }: { isOpen: boolean; onCancel: Function; afterSave: Function; parent_id?: string | null }) {
  const t = useTrans('label.accounts,otr.common');
  const { fields } = useFlexField('CUSTOMER');
  fields.forEach((field) => (initFormData.flex_fields[field.id] = field.default_value || ''));
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);
  const [isChildAccount, setIsChildAccount] = useState(false);
  const [createType, setCreateType] = useState('exist');
  const [formType, setFormType] = useState<'create-new' | 'select-from-existing'>('select-from-existing');
  const [existingAccount, setExistingAccount] = useState('');
  const [existingContact, setExistingContact] = useState('');
  const [contactData, setContactData] = useState(initContactFormData);
  const [createdCustomerId, setCreatedCustomerId] = useState('');
  const [finalResponse, setFinalResponse] = useState(null as any);

  useEffect(() => {
    onFormChange('parent_id', parent_id);
    if (parent_id === null) {
      setFormType('create-new');
    } else {
      onFormChange('type', 'Corporate');
    }
  }, [parent_id]);

  const onFormChange = (name: string, value: any, fieldType: string = 'basic_fields') => {
    setFormData((prevFormData) => {
      if (fieldType === 'basic_fields') {
        const updatedBasicFields = {
          ...prevFormData,
          [name]: value,
        };

        return updatedBasicFields;
      } else {
        return {
          ...prevFormData,
          flex_fields: {
            ...prevFormData.flex_fields,
            [name]: value,
          },
        };
      }
    });
  };

  const onContactFormChange = (name: string, value: any) => {
    setContactData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    onSubmit(e as any);
  };

  const tBe = useTrans('be.msg,be.error,be.attri');

  const saveCustomerContact = async (custId: string, callback: any) => {
    let responseData;

    try {
      if (createType === 'exist') {
        responseData = await createCustomerContacts(custId, { contact_id: existingContact, is_primary: true });

        if (responseData?.status_code === 417) {
          printError(responseData.result, form.select_contact.store, tBe);
          return;
        }
      } else {
        const cResponse = await createContact(contactData);

        if (cResponse.status_code === 417) {
          printError(cResponse.result, form.add_contact.store, tBe);
          return;
        }

        if (cResponse.is_success) {
          responseData = await createCustomerContacts(custId, { contact_id: cResponse.result.id, is_primary: true });
        }
      }

      if (responseData?.is_success) {
        callback();
      }
    } catch (error) {
      console.error('Error in saveCustomerContact:', error);
    }
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.customres_crud.store);
    clearError(form.contact_crud.store);
    clearError(form.select_contact.store);
    clearError(form.add_contact.store);
    setIsFormProcessing(true);

    try {
      if (createdCustomerId === '') {
        let responseData;

        if (formType === 'create-new') {
          responseData = await createCustomers(formData); //38
        } else {
          responseData = await createHierarchies(parent_id, { child_id: existingAccount, parent_id: parent_id }); //45
        }

        if (responseData && responseData.status_code === 417) {
          printError(responseData.result, form.customres_crud.store, tBe);
          setIsFormProcessing(false);
          return;
        }

        if (responseData && responseData.is_success) {
          setCreatedCustomerId(formType === 'create-new' ? responseData.result.id : existingAccount);
          if (formType === 'create-new') {
            saveCustomerContact(formType === 'create-new' ? responseData.result.id : existingAccount, () => toaster.success(tBe(responseData.message), afterSave()));
          } else {
            toaster.success(tBe(responseData.message), afterSave());
          }
          setFinalResponse(responseData);
        }
      } else {
        if (formType === 'create-new') {
          saveCustomerContact(createdCustomerId, () => toaster.success(tBe(finalResponse && finalResponse.message), afterSave()));
        }
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }

    setIsFormProcessing(false);
  }

  return (
    <Modal isOpen={isOpen} size="lg" scrollable>
      <ModalHeader title={t('add_new_entity', { entity: t('account') })} onClose={() => onCancel()} />
      {/* <form onSubmit={onSubmit} id={`${form.customres_crud.store}`}> */}
      <ModalBody>
        {parent_id !== null && (
          <div className="col-12 d-flex align-items-center gap-4 mb-3">
            <div className="d-flex align-items-center gap-1">
              <Input
                type="radio"
                id="select-from-existing"
                name="form_type"
                value="close"
                className="mb-2"
                checked={formType === 'select-from-existing'}
                onChange={() => setFormType('select-from-existing')}
              />
              <Label htmlFor="select-from-existing" label={t('select_from_accounts')} />
            </div>
            <div className="d-flex align-items-center gap-1">
              <Input type="radio" id="create-new" name="form_type" checked={formType === 'create-new'} onChange={() => setFormType('create-new')} value="another" className="mb-2" />
              <Label htmlFor="create-new" label={t('add_new_entity', { entity: t('accounts') })} />
            </div>
          </div>
        )}

        {formType === 'select-from-existing' ? (
          <form id={`${form.select_customer.store}`}>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="account" label={t('account')} isRequired />
              <AsyncSelect
                onChange={(value) => setExistingAccount(value)}
                className="form-control error-child_id"
                option={{ label: 'name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllCustomers(searchValue, currentPage)}
              />
            </div>
          </form>
        ) : (
          <>
            <form id={`${form.customres_crud.store}`}>
              {parent_id === null && (
                <>
                  <div className="col-12 col-md-6 mb-3 custom-select">
                    <Label label={t('account_type')} isRequired />
                    <Select
                      onChange={(value) => onFormChange('type', value)}
                      options={[
                        { label: t('corporate'), value: 'Corporate' },
                        { label: t('personal'), value: 'Personal' },
                      ]}
                      option={{ label: 'label', value: 'value' }}
                      isSearchable={false}
                      className="form-control error-type"
                    />
                    {/* <span className="error-type"></span> */}
                  </div>
                  <div className="mb-3">
                    <input
                      type="checkbox"
                      checked={isChildAccount}
                      onChange={(e) => {
                        const checked = e.target.checked;
                        setIsChildAccount(checked);

                        // Reset parent_id if unchecked
                        if (!checked) {
                          onFormChange('parent_id', null);
                        }
                      }}
                    />
                    <span className="ms-2 fs-14">This is a Child Account</span>
                  </div>
                </>
              )}

              {parent_id === null && isChildAccount && (
                <div className="col-12 col-md-6 mb-3 custom-select">
                  <Label htmlFor="parent_id" label={t('parent_account')} />
                  <AsyncSelect
                    onChange={(value) => onFormChange('parent_id', value)}
                    className="form-control error-parent_id"
                    option={{ label: 'name', value: 'id' }}
                    isSearchable={true}
                    loadOptions={fetchAllCustomers}
                  />
                </div>
              )}
              <div className="row">
                <div className="col-12 col-md-6 mb-3">
                  <Input isRequired label={t('account_name')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
                </div>
                <div className="col-12 col-md-6 mb-3">
                  <Input label={t('email')} value={formData.email} onChange={(e) => onFormChange('email', e.target.value)} className="form-control error-email" name="email" />
                </div>
                <div className="col-12 col-md-6 mb-3">
                  <Input label={t('address')} value={formData.address} onChange={(e) => onFormChange('address', e.target.value)} className="form-control error-address" name="address" />
                </div>
                <div className="col-12 col-md-6 mb-3">
                  <Input
                    type="url"
                    label={t('website')}
                    value={formData.website_url}
                    onChange={(e) => onFormChange('website_url', e.target.value)}
                    className="form-control error-website_url"
                    name="website_url"
                  />
                </div>
                <div className="col-12 col-md-6 mb-3">
                  <Label label={t('primary_contact_number')} isRequired />
                  <PhoneInput
                    country={'lk'}
                    enableAreaCodes={true}
                    value={formData.primary_contact}
                    inputStyle={{ height: '40px', width: '100%' }}
                    containerStyle={{ height: '40px', width: '100%' }}
                    onChange={(phone) => onFormChange('primary_contact', phone)}
                    inputClass="form-control error-primary_contact"
                    countryCodeEditable={false}
                  />
                  {/* <div className="error-primary_contact"></div> */}
                </div>
                <div className="col-12 col-md-6 mb-3">
                  <Label label={t('secondary_contact_number')} />
                  <PhoneInput
                    country={'lk'}
                    enableAreaCodes={true}
                    value={formData.secondary_contact}
                    inputStyle={{ height: '40px', width: '100%' }}
                    containerStyle={{ height: '40px', width: '100%' }}
                    onChange={(phone) => onFormChange('secondary_contact', phone)}
                    inputClass="form-control error-primary_contact_id"
                    countryCodeEditable={false}
                  />
                </div>
                {fields.map((field, index) => (
                  <div key={index} className="col-12 col-md-6 mb-3">
                    <FlexField field={field} value={formData.flex_fields[field.id]} onChange={(name: string, value: any) => onFormChange(name, value, 'flex_fields')} />
                  </div>
                ))}
                <div className="col-12 col-md-6 mb-3">
                  <Input
                    label={t('remarks')}
                    value={formData.remarks}
                    onChange={(e) => onFormChange('remarks', e.target.value)}
                    className="form-control error-remarks"
                    name="remarks"
                    type="textarea"
                  />
                </div>
              </div>
            </form>
            <div className="mt-3">
              {/* <form id={`${form.contact_crud.store}`}> */}
              <div className="fw-semibold mb-2">{t('primary_contact_person')}</div>
              <div>
                <div className="col-12 d-flex align-items-center gap-4 mb-3">
                  <div className="d-flex align-items-center gap-1">
                    <Input type="radio" id="exist" name="cus_select" value="exist" className="mb-2 pointer" checked={createType === 'exist'} onChange={(e: any) => setCreateType(e.target.value)} />
                    <Label htmlFor="exist" label={t('select_from_contacts')} />
                  </div>
                  <div className="d-flex align-items-center gap-1">
                    <Input type="radio" id="new" name="cus_select" checked={createType === 'new'} onChange={(e: any) => setCreateType(e.target.value)} value="new" className="mb-2 pointer" />
                    <Label htmlFor="new" label={t('add_new_entity', { entity: t('contacts') })} />
                  </div>
                </div>

                {createType === 'exist' ? (
                  <form id={`${form.select_contact.store}`}>
                    <div className="col-12 col-md-6 mb-3 custom-select">
                      <Label htmlFor="contacts" label={t('contacts')} isRequired />
                      <AsyncSelect
                        onChange={(value) => setExistingContact(value)}
                        className="form-control error-contact_id"
                        option={{ label: 'name', value: 'id' }}
                        isSearchable={true}
                        loadOptions={fetchContacts}
                      />
                    </div>
                  </form>
                ) : (
                  <>
                    <form id={`${form.add_contact.store}`}>
                      <div className="row">
                        <div className="col-12 col-md-6 mb-3">
                          <Input
                            isRequired
                            label={t('contact_person_name')}
                            value={contactData.name}
                            onChange={(e) => onContactFormChange('name', e.target.value)}
                            className="form-control error-name"
                            name="name"
                          />
                        </div>
                        <div className="col-12 col-md-6 mb-3">
                          <Input
                            label={t('address')}
                            value={contactData.address}
                            onChange={(e) => onContactFormChange('address', e.target.value)}
                            className="form-control error-address"
                            name="address"
                          />
                        </div>
                        <div className="col-12 col-md-6 mb-3">
                          <Input
                            label={t('email_address')}
                            value={contactData.email}
                            onChange={(e) => onContactFormChange('email', e.target.value)}
                            className="form-control error-email"
                            name="email"
                          />
                        </div>
                        <div className="col-12 col-md-6 mb-3">
                          <Input
                            label={t('remarks')}
                            value={contactData.remarks}
                            onChange={(e) => onContactFormChange('remarks', e.target.value)}
                            className="form-control error-remarks"
                            name="remarks"
                          />
                        </div>
                      </div>
                      <div>
                        <div className="row">
                          <div className="col-12 col-md-6 mb-3">
                            <Label label={t('primary_contact_number')} isRequired />
                            <PhoneInput
                              country={'lk'}
                              enableAreaCodes={true}
                              value={contactData.primary_contact}
                              inputStyle={{ height: '40px', width: '100%' }}
                              containerStyle={{ height: '40px', width: '100%' }}
                              onChange={(phone) => onContactFormChange('primary_contact', phone)}
                              inputClass="form-control error-primary_contact"
                              countryCodeEditable={false}
                            />
                          </div>
                          <div className="col-12 col-md-6 mb-3">
                            <Label label={t('secondary_contact_number')} />
                            <PhoneInput
                              country={'lk'}
                              enableAreaCodes={true}
                              value={contactData.secondary_contact}
                              inputStyle={{ height: '40px', width: '100%' }}
                              containerStyle={{ height: '40px', width: '100%' }}
                              onChange={(phone) => onContactFormChange('secondary_contact', phone)}
                              inputClass="form-control error-secondary_contact_id"
                              countryCodeEditable={false}
                            />
                          </div>
                        </div>
                      </div>
                    </form>
                  </>
                )}
              </div>
              {/* </form> */}
            </div>
          </>
        )}
      </ModalBody>

      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('create')} type="button" width="sm" isLoading={isFormProcessing} onClick={handleClick} />
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
      {/* </form> */}
    </Modal>
  );
}

export default AccountsCreate;
