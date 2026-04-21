import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { FormEvent, useEffect, useState } from 'react';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { useTrans } from '@/helpers/services/lang/langService';
import { getOneContacts, updateContacts } from '../../api-service';
import { IContacts, initFormData } from '../../model';
import { clearError } from '@/helpers/handlers/validationErrorHandler';
import ReactPhoneInput from '@/components/others/page-related/ReactPhoneInput';

export const ContactEdit = ({ isOpen, editId, afterUpdate, onCancel }: { isOpen: boolean; editId: string; onCancel: Function; afterUpdate: Function }) => {
  const t = useTrans('label.contacts,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);
  const [skeleton, setSkeleton] = useState(true);
  const [phoneVal, setPhoneVal] = useState('');
  // const [phoneIsValid, setPhoneIsValid] = useState(true);
  // const [phoneErrorMessage, setPhoneErrorMessage] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneContacts(editId);

      if (responseData?.is_success) {
        const data: IContacts = responseData.result;
        onFormChange('title', data.title);
        onFormChange('name', data.name);
        onFormChange('address', data.address);
        onFormChange('email', data.email);
        onFormChange('primary_contact', data.primary_contact);
        onFormChange('secondary_contact', data.secondary_contact);
        onFormChange('remarks', data.remarks);
        setPhoneVal(data.primary_contact);
        setSkeleton(false);

        // if (data.primary_contact) {
        //   validatePhoneNumber(data.primary_contact, getCountryFromPhone(data.primary_contact));
        // }
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

  // const getCountryFromPhone = (phone: string) => {
  //   return phone;
  // };

  // const validatePhoneNumber = (phone: string, countryCode: string) => {
  //   if (!phone || phone.length === 0) {
  //     setPhoneIsValid(false);
  //     return false;
  //   }

  //   try {
  //     const fullNumber = phone.startsWith('+') ? phone : `+${phone}`;
  //     const dialCode = phone.substring(0, phone.length - 9);
  //     const nationalNumber = phone.substring(dialCode.length);
  //     const isLongEnough = nationalNumber.length >= 7;

  //     if (!isLongEnough) {
  //       setPhoneIsValid(false);
  //       return false;
  //     }

  //     const isValid = isValidPhoneNumber(fullNumber, countryCode.toUpperCase() as any);

  //     setPhoneIsValid(isValid);
  //     if (!isValid) {
  //       setPhoneErrorMessage('Invalid phone number format for this country');
  //     } else {
  //       setPhoneErrorMessage('');
  //     }

  //     return isValid;
  //   } catch (error) {
  //     setPhoneIsValid(false);
  //     setPhoneErrorMessage('Invalid phone number');
  //     return false;
  //   }
  // };

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.contact_crud.update);

    // const isPhoneValid = validatePhoneNumber(formData.primary_contact, formData.primary_contact ? getCountryFromPhone(formData.primary_contact) : 'lk');

    setIsFormProcessing(true);

    try {
      const responseData = await updateContacts(editId, formData);
      setIsFormProcessing(false);
      // if (responseData.status_code === 417 || isPhoneValid) {
      //   printError(responseData.result, form.contact_crud.update, tBe);
      // }
      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setFormData(initFormData);
        onCancel();
        afterUpdate();
      }
    } catch (error) {
      console.error('An error occurred:', error);
      setIsFormProcessing(false);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('edit_entity', { entity: t('contact') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.contact_crud.update}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('contact_person_name')} isRequired />
              {skeleton ? <InputSkeleton /> : <Input value={formData.name || ''} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('address')} />
              {skeleton ? <InputSkeleton /> : <Input value={formData.address || ''} onChange={(e) => onFormChange('address', e.target.value)} className="form-control error-address" name="address" />}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('email_address')} />
              {skeleton ? <InputSkeleton /> : <Input value={formData.email || ''} onChange={(e) => onFormChange('email', e.target.value)} className="form-control error-email" name="email" />}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('remarks')} />
              {skeleton ? <InputSkeleton /> : <Input value={formData.remarks || ''} onChange={(e) => onFormChange('remarks', e.target.value)} className="form-control error-remarks" name="remarks" />}
            </div>
          </div>
          <div>
            <div className="fw-semibold mb-2">{t('contact')}</div>
            <div className="row">
              <div className="col-12 col-md-6 mb-3">
                <Label label={t('primary_contact_number')} isRequired />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  <ReactPhoneInput
                    value={phoneVal}
                    onChange={(phone) => onFormChange('primary_contact', phone)}
                    defaultCountryCode={'lk'}
                    enableAreaCodes={false}
                    className="form-control error-primary_contact"
                  />
                  // <div>
                  //   <PhoneInput
                  //     country={'lk'}
                  //     enableAreaCodes={true}
                  //     value={phoneVal}
                  //     inputStyle={{ height: '40px', width: '100%' }}
                  //     containerStyle={{ height: '40px', width: '100%' }}
                  //     onChange={(phone, data: import('react-phone-input-2').CountryData) => {
                  //       if (phone === data?.dialCode) {
                  //         onFormChange('primary_contact', '');
                  //         setPhoneIsValid(false);
                  //         setPhoneErrorMessage('The Primary Contact field is required.');
                  //       } else {
                  //         onFormChange('primary_contact', phone);
                  //         setPhoneVal(phone);

                  //         try {
                  //           const fullNumber = phone.startsWith('+') ? phone : `+${phone}`;
                  //           const nationalNumber = phone.substring(data.dialCode.length);
                  //           const isLongEnough = nationalNumber.length >= 7;

                  //           if (!isLongEnough) {
                  //             setPhoneIsValid(false);
                  //             setPhoneErrorMessage('Phone number is too short');
                  //             return;
                  //           }

                  //           const isValid = isValidPhoneNumber(fullNumber, data.countryCode.toUpperCase() as import('libphonenumber-js').CountryCode);

                  //           setPhoneIsValid(isValid);
                  //           if (!isValid) {
                  //             setPhoneErrorMessage('Invalid phone number format for this country');
                  //           } else {
                  //             setPhoneErrorMessage('');
                  //           }
                  //         } catch (error) {
                  //           setPhoneIsValid(false);
                  //           setPhoneErrorMessage('Invalid phone number');
                  //         }
                  //       }
                  //     }}
                  //     inputClass="form-control"
                  //     countryCodeEditable={false}
                  //   />
                  //   {!phoneIsValid && phoneErrorMessage && (
                  //     <strong className="fw-bold fs-13" style={{ color: '#dc3545' }}>
                  //       {phoneErrorMessage}
                  //     </strong>
                  //   )}
                  // </div>
                )}
              </div>
              <div className="col-12 col-md-6 mb-3">
                <Label label={t('secondary_contact_number')} />
                {skeleton ? (
                  <InputSkeleton />
                ) : (
                  // <PhoneInput
                  //   country={'lk'}
                  //   enableAreaCodes={true}
                  //   value={formData.secondary_contact}
                  //   inputStyle={{ height: '40px', width: '100%' }}
                  //   containerStyle={{ height: '40px', width: '100%' }}
                  //   onChange={(phone) => onFormChange('secondary_contact', phone)}
                  //   countryCodeEditable={false}
                  // />
                  <ReactPhoneInput
                    value={formData.secondary_contact}
                    onChange={(phone) => onFormChange('secondary_contact', phone)}
                    defaultCountryCode={'lk'}
                    enableAreaCodes={false}
                    className="form-control error-secondary_contact"
                  />
                )}
              </div>
            </div>
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
