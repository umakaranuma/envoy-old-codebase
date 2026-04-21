import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import { initContactFormData } from '../_utils/model';
import { toaster } from '@/helpers/services/toaster';
import { createContact, createCustomerContacts } from '../_utils/api-service';
import { useTrans } from '@/helpers/services/lang/langService';
import { AsyncSelect } from '@apptimus-ui/select';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { fetchContacts } from '../_utils/services';
import { systemCodes } from '@/constans/Common';
import ReactPhoneInput from '@/components/others/page-related/ReactPhoneInput';

function ContactCreate({ isOpen, onCancel, afterSave, id }: { isOpen: boolean; onCancel: Function; afterSave: Function; id: string }) {
  const t = useTrans('label.accounts,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initContactFormData);
  const [createType, setCreateType] = useState('exist');

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmitExist() {
    clearError(form.contact_crud.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createCustomerContacts(id, { contact_id: formData.contact_id, is_primary: false });
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.contact_crud.store, tBe);
      }

      if (responseData.system_code === systemCodes.CUSTOMER_CONTACT_ALREADY_ADDED) {
        toaster.success(tBe(responseData.message));
      }

      if (responseData.is_success) {
        afterSave();
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  async function onSubmit() {
    clearError(form.contact_crud.store);

    setIsFormProcessing(true);

    try {
      const responseData = await createContact(formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.contact_crud.store, tBe);
      }

      if (responseData.is_success) {
        const response = await createCustomerContacts(id, { contact_id: responseData.result.id, is_primary: false });

        if (responseData.system_code === systemCodes.CUSTOMER_CONTACT_ALREADY_ADDED) {
          toaster.success(tBe(responseData.message));
        }

        if (response.is_success) {
          afterSave();
          toaster.success(tBe(responseData.message));
        }
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen} size="lg">
      <ModalHeader title={t('add_contact')} onClose={() => onCancel()} />
      <ModalBody>
        <>
          <div className="col-12 d-flex align-items-center gap-4 mb-3">
            <div className="d-flex align-items-center gap-1">
              <Input type="radio" id="exist" name="cus_select" value="exist" className="mb-2 pointer" checked={createType === 'exist'} onChange={(e: any) => setCreateType(e.target.value)} />
              <Label htmlFor="html" label={t('select_from_contacts')} />
            </div>
            <div className="d-flex align-items-center gap-1">
              <Input type="radio" id="new" name="cus_select" checked={createType === 'new'} onChange={(e: any) => setCreateType(e.target.value)} value="new" className="mb-2 pointer" />
              <Label htmlFor="new" label={t('add_new_entity', { entity: t('contacts') })} />
            </div>
          </div>
          {createType === 'exist' ? (
            <form id={`${form.contact_crud.store}`}>
              <div className="col-12 col-md-6 mb-3 custom-select">
                <Label htmlFor="contacts" label={t('contacts')} isRequired />
                <AsyncSelect
                  onChange={(value) => onFormChange('contact_id', value)}
                  className="form-control error-contact_id"
                  option={{ label: 'name', value: 'id' }}
                  isSearchable={true}
                  loadOptions={fetchContacts}
                />
              </div>
            </form>
          ) : (
            <form id={`${form.contact_crud.store}`}>
              <div className="row">
                <div className="col-12 col-md-6 mb-3">
                  <Input isRequired label={t('contact_person_name')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
                </div>
                <div className="col-12 col-md-6 mb-3">
                  <Input label={t('address')} value={formData.address} onChange={(e) => onFormChange('address', e.target.value)} className="form-control error-address" name="address" />
                </div>
                <div className="col-12 col-md-6 mb-3">
                  <Input label={t('email_address')} value={formData.email} onChange={(e) => onFormChange('email', e.target.value)} className="form-control error-email" name="email" />
                </div>
                <div className="col-12 col-md-6 mb-3">
                  <Input label={t('remarks')} value={formData.remarks} onChange={(e) => onFormChange('remarks', e.target.value)} className="form-control error-remarks" name="remarks" />
                </div>
              </div>
              <div>
                <div className="row">
                  <div className="col-12 col-md-6 mb-3">
                    <Label label={t('primary_contact_number')} isRequired />
                    {/* <PhoneInput
                      country={'lk'}
                      enableAreaCodes={true}
                      value={formData.primary_contact}
                      inputStyle={{ height: '40px', width: '100%' }}
                      containerStyle={{ height: '40px', width: '100%' }}
                      onChange={(phone) => onFormChange('primary_contact', phone)}
                      inputClass="form-control error-primary_contact"
                      countryCodeEditable={false}
                    /> */}
                    <ReactPhoneInput
                      value={formData.primary_contact}
                      onChange={(phone) => onFormChange('primary_contact', phone)}
                      defaultCountryCode={'lk'}
                      enableAreaCodes={false}
                      className="form-control error-primary_contact"
                    />
                  </div>
                  <div className="col-12 col-md-6 mb-3">
                    <Label label={t('secondary_contact_number')} />
                    {/* <PhoneInput
                      country={'lk'}
                      enableAreaCodes={true}
                      value={formData.secondary_contact}
                      inputStyle={{ height: '40px', width: '100%' }}
                      containerStyle={{ height: '40px', width: '100%' }}
                      onChange={(phone) => onFormChange('secondary_contact', phone)}
                      inputClass="form-control error-primary_contact_id"
                      countryCodeEditable={false}
                    /> */}
                    <ReactPhoneInput
                      value={formData.secondary_contact}
                      onChange={(phone) => onFormChange('secondary_contact', phone)}
                      defaultCountryCode={'lk'}
                      enableAreaCodes={false}
                      className="form-control error-secondary_contact"
                    />
                  </div>
                </div>
              </div>
            </form>
          )}
        </>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('add')} type="submit" width="sm" onClick={createType === 'exist' ? onSubmitExist : onSubmit} isLoading={isFormProcessing} />
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default ContactCreate;
