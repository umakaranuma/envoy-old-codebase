'use client';
import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { initCPartner } from '../model';
import { createPartner } from '../api-service';
import LogoUploader from '@/components/others/page-related/LogoUploader';
import { Select } from '@apptimus-ui/select';
import { handleFileUpload } from '@/helpers/services/commonService';
import ReactPhoneInput from '@/components/others/page-related/ReactPhoneInput';

export function CreatePartner({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const t = useTrans('label.partners,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initCPartner);
  const [resource, setResource] = useState<File | null>(null);
  // const [uploadedFileKey, setUploadedFileKey] = useState<string | null>(null);
  const [defaultValue, setDefaultValue] = useState({});

  useEffect(() => {
    setDefaultValue({ label: t('mr'), value: 'Mr.' });
    onFormChange('contact_title', 'Mr.');
  }, []);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    clearError(form.partner.store);
    setIsFormProcessing(true);

    try {
      // if (resource && (!uploadedFileKey || resource.name !== uploadedFileKey)) {
      //   const docData = await handleFileUpload(resource);
      //   setUploadedFileKey(resource.name);
      //   onFormChange('logo', docData);
      // }
      // onFormChange('is_primary', true);
      // onFormChange('status_id', '1');
      const docData = await handleFileUpload(resource, 'partner', 'core/partner');
      const responseData = await createPartner({ ...formData, logo: docData?.key, is_primary: true, status_id: 1 });
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.partner.store, tBe);
      }

      if (responseData.is_success) {
        afterSave();
        setResource(null);
        setFormData(initCPartner);
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  //   if (!resource) {
  //     return null;
  //   }
  //   try {
  //     const uploadFormData = new FormData();
  //     uploadFormData.append('file', resource);
  //     const key = await fileUploader(uploadFormData, 'envoy-partner');
  //     return key;
  //   } catch (error) {
  //     console.error('Error uploading file:', error);
  //     toaster.error('file_upload_failed');
  //     throw error;
  //   }
  // };
  return (
    <Modal isOpen={isOpen} scrollable size="xl">
      <ModalHeader title={t('add_new_entity', { entity: t('partner') })} onClose={() => onCancel()} />
      <ModalBody>
        <div id={`${form.partner.store}`}>
          {/* Basic Information Section */}
          <div className="row mb-4">
            <div className="col-12 col-md-12 col-lg-2 mb-2">
              <Label htmlFor="logo" label={t('logo')} />
              <LogoUploader
                width={140}
                height={130}
                cropShape={'rect'}
                onChange={(selectedFiles: any) => {
                  setResource(selectedFiles);
                }}
              />
            </div>
            <div className="col-12 col-md-10">
              <div className="row">
                <div className="col-12 col-md-4 mb-4">
                  <Input isRequired label={t('partner_name')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
                </div>
                <div className="col-12 col-md-4 mb-4">
                  <Input isRequired label={t('email')} value={formData.email} onChange={(e) => onFormChange('email', e.target.value)} className="form-control error-email" name="email" />
                </div>
                <div className="col-12 col-md-4 mb-4">
                  <Label label={t('contact_number')} isRequired />
                  {/* <CustomPhoneInput
                    value={formData.contact_number}
                    onChange={(phone) => {
                      onFormChange('contact_number', phone);
                    }}
                  /> */}
                  {/* <PhoneInput
                    country={'lk'}
                    enableAreaCodes={true}
                    value={formData.contact_number}
                    inputStyle={{ height: '40px', width: '100%' }}
                    containerStyle={{ height: '40px', width: '100%' }}
                    onChange={(phone) => onFormChange('contact_number', phone)}
                    inputClass="form-control error-contact_number"
                    countryCodeEditable={false}
                  /> */}
                  <ReactPhoneInput
                    value={formData.contact_number}
                    onChange={(phone) => onFormChange('contact_number', phone)}
                    defaultCountryCode={'lk'}
                    enableAreaCodes={false}
                    className="form-control error-contact_number"
                  />
                </div>
              </div>
              <div className="row">
                <div className="col-12 col-md-4 mb-2">
                  <Input type="number" label={t('fax_number')} value={formData.fax_no} onChange={(e) => onFormChange('fax_no', e.target.value)} className="form-control error-fax_no" name="fax_no" />
                </div>
                <div className="col-12 col-md-4 mb-2">
                  <Input isRequired label={t('address')} value={formData.address} onChange={(e) => onFormChange('address', e.target.value)} className="form-control error-address" name="address" />
                </div>
                <div className="col-12 col-md-4 mb-2">
                  <Input label={t('website')} value={formData.website} onChange={(e) => onFormChange('website', e.target.value)} className="form-control error-website" name="website" />
                </div>
              </div>
            </div>
          </div>

          {/* Primary Contact Section */}
          <div className="row">
            <div className="col-12">
              <div className="panel-title mb-2">{t('primary_contact')}</div>
            </div>
            <div className="col-12 col-md-4 mb-2">
              <Label label={t('contact_type')} isRequired />
              <Select
                onChange={(_, data) => {
                  onFormChange('contact_type', data.value);
                }}
                options={[
                  { label: t('primary'), value: 'primary' },
                  { label: t('secondary'), value: 'secondary' },
                ]}
                option={{ label: 'label', value: 'value' }}
                isSearchable={false}
                className="form-control error-contact_type p-0"
                defaultValue={{ label: formData.contact_type.charAt(0).toUpperCase() + formData.contact_type.slice(1), value: formData.contact_type }}
              />
            </div>
            <div className="col-12 col-md-4 mb-2">
              <Label label={t('salutation')} isRequired />
              <Select
                onChange={(_, data) => {
                  onFormChange('contact_title', data.value);
                  setDefaultValue(data);
                }}
                options={[
                  { label: t('mr'), value: 'Mr.' },
                  { label: t('mrs'), value: 'Mrs.' },
                  { label: t('miss'), value: 'Miss.' },
                  { label: t('rev'), value: 'Rev.' },
                ]}
                option={{ label: 'label', value: 'value' }}
                isSearchable={false}
                className="form-control error-contact_title p-0"
                defaultValue={defaultValue}
              />
            </div>
            <div className="col-12 col-md-4 mb-2">
              <Input
                isRequired
                label={t('contact_person_name')}
                value={formData.contact_name}
                onChange={(e) => onFormChange('contact_name', e.target.value)}
                className="form-control error-contact_name"
                name="contact_name"
              />
            </div>
            <div className="col-12 col-md-4 mb-2">
              <Input label={t('role')} value={formData.contact_role} onChange={(e) => onFormChange('contact_role', e.target.value)} className="form-control error-contact_role" name="contact_role" />
            </div>
          </div>
          <div className="row">
            <div className="col-12 col-md-4 mb-2">
              <Input
                label={t('email')}
                value={formData.contact_email}
                onChange={(e) => onFormChange('contact_email', e.target.value)}
                className="form-control error-contact_email"
                name="contact_email"
              />
            </div>
            <div className="col-12 col-md-4 mb-2">
              <Label label={t('contact_number')} isRequired />
              <ReactPhoneInput
                value={formData.contact_primary}
                onChange={(phone) => onFormChange('contact_primary', phone)}
                defaultCountryCode={'lk'}
                enableAreaCodes={false}
                className="form-control error-contact_primary"
              />
            </div>
            <div className="col-12 col-md-4 mb-2">
              <Input
                type="textarea"
                label={t('remarks')}
                value={formData.contact_remarks}
                onChange={(e) => onFormChange('contact_remarks', e.target.value)}
                className="form-control error-contact_remarks"
                name="contact_remarks"
              />
            </div>
          </div>

          {/* Bank Account Information Section */}
          <div className="row">
            <div className="col-12">
              <div className="panel-title mb-2">{t('bank_account_info')}</div>
            </div>
            <div className="col-12 col-md-4 mb-2">
              <Input
                label={t('account_holder_name')}
                value={formData.account_holder_name}
                onChange={(e) => onFormChange('account_holder_name', e.target.value)}
                className="form-control error-account_holder_name"
                name="account_holder_name"
              />
            </div>
            <div className="col-12 col-md-4 mb-2">
              <Input label={t('bank_name')} value={formData.bank_name} onChange={(e) => onFormChange('bank_name', e.target.value)} className="form-control error-bank_name" name="bank_name" />
            </div>
            <div className="col-12 col-md-4 mb-2">
              <Input
                type="text"
                label={t('account_number')}
                value={formData.account_number}
                onChange={(e) => {
                  onFormChange('account_number', e.target.value);
                }}
                className="form-control error-account_number"
                name="account_number"
              />
            </div>
          </div>
          <div className="row mb-4">
            <div className="col-12 col-md-4 mb-2">
              <Input
                label={t('bank_branch')}
                value={formData.bank_branch}
                onChange={(e) => onFormChange('bank_branch', e.target.value)}
                className="form-control error-bank_branch"
                name="bank_branch"
              />
            </div>
            <div className="col-12 col-md-4 mb-2">
              <Input
                type="number"
                label={t('isbn_swift_code')}
                value={formData.iban_swift_code}
                onChange={(e) => onFormChange('iban_swift_code', e.target.value)}
                className="form-control error-iban_swift_code"
                name="isbn_swift_code"
              />
            </div>
            <div className="col-12 col-md-4 mb-2">
              <Input
                label={t('payment_gateway_url')}
                value={formData.payment_gateway_url}
                onChange={(e) => onFormChange('payment_gateway_url', e.target.value)}
                className="form-control error-payment_gateway_url"
                name="payment_gateway_url"
              />
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
