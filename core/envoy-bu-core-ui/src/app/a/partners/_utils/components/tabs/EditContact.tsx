import { form } from '@/constans/Form';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import React, { useEffect, useState } from 'react';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { initialContactDetail } from '../../model';
import { getOnePartnerContact, updatePartnerContact } from '../../api-service';
import { useParams } from 'next/navigation';
import { toaster } from '@/helpers/services/toaster';
import ReactPhoneInput from '@/components/others/page-related/ReactPhoneInput';

function EditContact({ isOpen, onCancel, afterSave, editId }: { isOpen: boolean; onCancel: () => void; afterSave: () => void; editId: string }) {
  const t = useTrans('label.partners,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const params = useParams();
  const partnerId = params.partnerId?.toString() || '';
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initialContactDetail);
  const [skeleton, setSkeleton] = useState(true);
  // const [defaultValue, setDefaultValue] = useState({});
  // const [PhoneData, setPhoneData] = useState<CountryData | undefined>(undefined);

  // const titleOptions = [
  //   { label: t('mr'), value: 'Mr.' },
  //   { label: t('mrs'), value: 'Mrs.' },
  //   { label: t('miss'), value: 'Miss.' },
  //   { label: t('rev'), value: 'Rev.' },
  // ];

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOnePartnerContact(partnerId, editId);
      if (responseData?.is_success) {
        // const defaultOption = titleOptions.find((option) => option.value === responseData.result.title) || titleOptions[0];
        // setDefaultValue(defaultOption);
        setFormData({ ...responseData.result, title: responseData.result.title || '' });
        setSkeleton(false);
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

  async function onSubmit() {
    clearError(form.partner_contact.update);
    setIsFormProcessing(true);

    try {
      // const dialCode = (PhoneData as CountryData)?.dialCode;
      // const nationalNumber = removeCountryCode(formData.primary_contact, dialCode);
      const responseData = await updatePartnerContact({ ...formData, primary_contact: formData.primary_contact }, partnerId, editId);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.partner_contact.update, tBe);
      }

      if (responseData.is_success) {
        afterSave();
        setFormData(initialContactDetail);
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  // const removeCountryCode = (phoneNumber: string, countryCode: string) => {
  //   if (!phoneNumber || !countryCode) return phoneNumber;

  //   // If phoneNumber is exactly the country code (with or without '+'), return empty
  //   if (phoneNumber === countryCode || phoneNumber === `+${countryCode}`) {
  //     return '';
  //   }

  //   // If phoneNumber starts with the country code (with '+'), return empty
  //   if (phoneNumber.startsWith(`+${countryCode}`)) {
  //     return '';
  //   }

  //   // Otherwise, return the original phone number
  //   return phoneNumber;
  // };

  return (
    <Modal
      isOpen={isOpen}
      onBackdrop={() => {
        onCancel();
      }}
      size={'lg'}
    >
      <ModalHeader title={t('edit_entity', { entity: t('contact') })} onClose={() => onCancel()} />
      <ModalBody>
        <div id={`${form.partner_contact.update}`}>
          <div className="row">
            {/* <div className="col-12 col-md-6 mb-3">
              <Label label={t('salutation')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Select
                  defaultValue={defaultValue}
                  onChange={(value) => onFormChange('title', value)}
                  options={titleOptions}
                  option={{ label: 'label', value: 'value' }}
                  isSearchable={false}
                  className="form-control error-title p-0"
                />
              )}
            </div> */}
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('contact_person_name')} isRequired />
              {skeleton ? <InputSkeleton /> : <Input value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('email')} isRequired />
              {skeleton ? <InputSkeleton /> : <Input value={formData.email} onChange={(e) => onFormChange('email', e.target.value)} className="form-control error-email" name="email" />}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('contact_number')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                // <PhoneInput
                //   country={'lk'}
                //   enableAreaCodes={true}
                //   value={formData.primary_contact}
                //   inputStyle={{ height: '40px', width: '100%' }}
                //   containerStyle={{ height: '40px', width: '100%' }}
                //   onChange={(value, country) => {
                //     onFormChange('primary_contact', value);
                //     setPhoneData(country as CountryData);
                //   }}
                //   inputClass="form-control error-primary_contact"
                //   countryCodeEditable={false}
                // />
                <ReactPhoneInput
                  value={formData.primary_contact}
                  onChange={(phone) => onFormChange('primary_contact', phone)}
                  defaultCountryCode={'lk'}
                  enableAreaCodes={false}
                  className="form-control error-primary_contact"
                />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('remarks')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input value={formData.remarks} onChange={(e) => onFormChange('remarks', e.target.value)} className="form-control error-remarks" name="remarks" type="textarea" />
              )}
            </div>
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('update')} onClick={onSubmit} width="sm" isLoading={isFormProcessing} />
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default EditContact;
