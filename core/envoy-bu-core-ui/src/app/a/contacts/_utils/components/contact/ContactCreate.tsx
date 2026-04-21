import { createContact } from '@/app/a/accounts/_utils/api-service';
import { initFormData } from '../../model';
import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import ReactPhoneInput from '@/components/others/page-related/ReactPhoneInput';

function ContactCreate({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const t = useTrans('label.contacts,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);
  // const [phoneIsValid, setPhoneIsValid] = useState(true);
  // const [secondaryPhoneIsValid, setSecondaryPhoneIsValid] = useState(true);
  // const [primaryPhoneErrorMessage, setPrimaryPhoneErrorMessage] = useState('');
  // const [secondaryPhoneErrorMessage, setSecondaryPrimaryPhoneErrorMessage] = useState('');

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.contact_crud.store);
    setIsFormProcessing(true);
    try {
      const responseData = await createContact(formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.contact_crud.store, tBe);
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
    <Modal isOpen={isOpen} size="lg" onBackdrop={() => onCancel()}>
      <ModalHeader title={t('add_contact_details')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.contact_crud.store}`}>
        <ModalBody>
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
            {/* <div className="fw-semibold mb-2">{t('contact')}</div> */}
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
                  // onChange={(phone, data: import('react-phone-input-2').CountryData) => {
                  //   if (phone === data?.dialCode) {
                  //     onFormChange('primary_contact', data?.dialCode);
                  //     setPhoneIsValid(false);
                  //     setPrimaryPhoneErrorMessage('The Primary Contact field is required.');
                  //   } else {
                  //     onFormChange('primary_contact', phone);

                  //     try {
                  //       const fullNumber = phone.startsWith('+') ? phone : `+${phone}`;
                  //       const nationalNumber = phone.substring(data.dialCode.length);
                  //       const isLongEnough = nationalNumber.length >= 7;

                  //       if (!isLongEnough) {
                  //         setPhoneIsValid(false);
                  //         setPrimaryPhoneErrorMessage('Phone number is too short');
                  //         return;
                  //       }

                  //       const isValid = isValidPhoneNumber(fullNumber, data.countryCode.toUpperCase() as import('libphonenumber-js').CountryCode);

                  //       setPhoneIsValid(isValid);
                  //       if (!isValid) {
                  //         setPrimaryPhoneErrorMessage('Invalid phone number format for this country');
                  //       } else {
                  //         setPrimaryPhoneErrorMessage('');
                  //       }
                  //     } catch (error) {
                  //       setPhoneIsValid(false);
                  //       setPrimaryPhoneErrorMessage('Invalid phone number');
                  //     }
                  //   }
                  // }}
                  // inputClass="form-control error-primary_contact"
                  countryCodeEditable={false}
                  inputClass="form-control error-primary_contact"
                /> */}
                <ReactPhoneInput
                  value={formData.primary_contact}
                  onChange={(phone) => onFormChange('primary_contact', phone)}
                  defaultCountryCode={'lk'}
                  enableAreaCodes={false}
                  className="form-control error-primary_contact"
                />
                {/* {!phoneIsValid && primaryPhoneErrorMessage && (
                  <strong className="fw-bold fs-13" style={{ color: '#dc3545' }}>
                    {primaryPhoneErrorMessage}
                  </strong>
                )} */}
              </div>
              <div className="col-12 col-md-6 mb-3">
                <Label label={t('secondary_contact_number')} />
                {/* <PhoneInput
                  country={'lk'}
                  enableAreaCodes={true}
                  value={formData.secondary_contact}
                  inputStyle={{ height: '40px', width: '100%' }}
                  containerStyle={{ height: '40px', width: '100%' }}
                  // onChange={(phone) => onFormChange('secondary_contact', phone)}
                  inputClass="form-control error-secondary_contact"
                  countryCodeEditable={false}
                  onChange={(phone) => onFormChange('secondary_contact', phone)}
                  // onChange={(phone, data: import('react-phone-input-2').CountryData) => {
                  //   if (phone === data?.dialCode) {
                  //     onFormChange('secondary_contact', '');
                  //     setSecondaryPhoneIsValid(true);
                  //   } else {
                  //     onFormChange('secondary_contact', phone);

                  //     try {
                  //       const fullNumber = phone.startsWith('+') ? phone : `+${phone}`;
                  //       const nationalNumber = phone.substring(data.dialCode.length);
                  //       const isLongEnough = nationalNumber.length >= 7;

                  //       if (!isLongEnough) {
                  //         setSecondaryPhoneIsValid(false);
                  //         setSecondaryPrimaryPhoneErrorMessage('Phone number is too short');
                  //         return;
                  //       }

                  //       const isValid = isValidPhoneNumber(fullNumber, data.countryCode.toUpperCase() as import('libphonenumber-js').CountryCode);

                  //       setSecondaryPhoneIsValid(isValid);
                  //       if (!isValid) {
                  //         setSecondaryPrimaryPhoneErrorMessage('Invalid phone number format for this country');
                  //       } else {
                  //         setSecondaryPrimaryPhoneErrorMessage('');
                  //       }
                  //     } catch (error) {
                  //       setSecondaryPhoneIsValid(false);
                  //       setSecondaryPrimaryPhoneErrorMessage('Invalid phone number');
                  //     }
                  //   }
                  // }}
                /> */}
                <ReactPhoneInput
                  value={formData.secondary_contact}
                  onChange={(phone) => onFormChange('secondary_contact', phone)}
                  defaultCountryCode={'lk'}
                  enableAreaCodes={false}
                  className="form-control error-secondary_contact"
                />
                {/* {!secondaryPhoneIsValid && secondaryPhoneErrorMessage && (
                  <strong className="fw-bold fs-13" style={{ color: '#dc3545' }}>
                    {secondaryPhoneErrorMessage}
                  </strong>
                )} */}
              </div>
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('create_a_contact')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default ContactCreate;
