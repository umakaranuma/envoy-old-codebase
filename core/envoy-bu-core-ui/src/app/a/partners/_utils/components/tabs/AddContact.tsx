import { form } from '@/constans/Form';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import React, { useState } from 'react';
import { initialContactDetail } from '../../model';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { Select } from '@apptimus-ui/select';
import { createPartnerContact } from '../../api-service';
import { toaster } from '@/helpers/services/toaster';
import { useParams } from 'next/navigation';
import ReactPhoneInput from '@/components/others/page-related/ReactPhoneInput';

function AddContact({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: () => void; afterSave: () => void }) {
  const t = useTrans('label.partners,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const params = useParams();
  const partnerId = params.partnerId?.toString() || '';
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initialContactDetail);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    clearError(form.partner_contact.store);
    setIsFormProcessing(true);
    try {
      const responseData = await createPartnerContact(formData, partnerId);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.partner_contact.store, tBe);
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

  return (
    <Modal
      isOpen={isOpen}
      onBackdrop={() => {
        onCancel();
      }}
      size={'lg'}
    >
      <ModalHeader title={t('add_new_entity', { entity: t('contact') })} onClose={() => onCancel()} />
      <ModalBody>
        <div id={`${form.partner_contact.store}`}>
          <div className="row">
            {/* <div className="col-12 col-md-6 mb-3">
              <Label label={t('salutation')} />
              <Select
                onChange={(value) => onFormChange('title', value)}
                options={[
                  { label: t('mr'), value: 'Mr.' },
                  { label: t('mrs'), value: 'Mrs.' },
                  { label: t('miss'), value: 'Miss.' },
                  { label: t('rev'), value: 'Rev.' },
                ]}
                option={{ label: 'label', value: 'value' }}
                isSearchable={false}
                className="form-control error-title p-0"
              />
            </div> */}
            <div className="col-12 col-md-6 mb-3">
              <Input isRequired label={t('contact_person_name')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input isRequired label={t('email')} value={formData.email} onChange={(e) => onFormChange('email', e.target.value)} className="form-control error-email" name="email" />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('contact_number')} isRequired />
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

            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('contact_level')} isRequired />
              <Select
                onChange={(value) => onFormChange('contact_type', value)}
                options={[
                  { label: t('primary'), value: 'primary' },
                  { label: t('secondary'), value: 'secondary' },
                  { label: t('other'), value: 'other' },
                ]}
                option={{ label: 'label', value: 'value' }}
                isSearchable={false}
                className="form-control error-contact_type"
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input type={'textarea'} label={t('remarks')} value={formData.remarks} onChange={(e) => onFormChange('remarks', e.target.value)} className="form-control error-remarks" name="remarks" />
            </div>
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('create')} onClick={onSubmit} width="sm" isLoading={isFormProcessing} />
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default AddContact;
