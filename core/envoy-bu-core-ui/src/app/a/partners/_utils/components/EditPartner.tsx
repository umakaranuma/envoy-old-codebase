'use client';
import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label, Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { initCPartner } from '../model';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { fileRemover } from '@/constans/storageService';
import { getOnePartner, updatePartner } from '../api-service';
import LogoUploader from '@/components/others/page-related/LogoUploader';
import { Select } from '@apptimus-ui/select';
import { handleFileUpload } from '@/helpers/services/commonService';
import ReactPhoneInput from '@/components/others/page-related/ReactPhoneInput';

export function EditPartner({ isOpen, onCancel, afterEdit, editId }: { isOpen: boolean; onCancel: Function; afterEdit: Function; editId: string }) {
  const t = useTrans('label.partners,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initCPartner);
  const [resource, setResource] = useState<File | null>();
  const [skeleton, setSkeleton] = useState(false);
  const [deletableResource, setDeletableResource] = useState<string | null>(null);
  const [defaultValue, setDefaultValue] = useState({});

  const titleOptions = [
    { label: t('mr'), value: 'Mr.' },
    { label: t('mrs'), value: 'Mrs.' },
    { label: t('miss'), value: 'Miss.' },
    { label: t('rev'), value: 'Rev.' },
  ];

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOnePartner(editId);
      if (responseData?.is_success) {
        const data = responseData.result;
        const formattedData = {
          name: data.name || '',
          logo: data.logo || '',
          address: data.address || '',
          contact_number: data.contact_no || '',
          email: data.email || '',
          website: data.website || '',
          fax_no: data.fax_no || '',

          // Bank details (take first bank detail if exists)
          account_holder_name: data.bank_details?.[0]?.account_holder_name || '',
          bank_name: data.bank_details?.[0]?.bank_name || '',
          bank_branch: data.bank_details?.[0]?.bank_branch || '',
          account_number: data.bank_details?.[0]?.account_number || '',
          iban_swift_code: data.bank_details?.[0]?.iban_swift_code || '',
          payment_gateway_url: data.bank_details?.[0]?.payment_gateway_url || '',

          // Contact details (take first contact detail if exists)
          contact_title: data.contact_details?.[0]?.title || '',
          contact_name: data.contact_details?.[0]?.name || '',
          contact_primary: data.contact_details?.[0]?.primary_contact || '',
          contact_email: data.contact_details?.[0]?.email || '',
          contact_remarks: data.contact_details?.[0]?.remarks || '',
          is_primary: data.contact_details?.[0]?.is_primary || false,
          contact_role: data.contact_details?.[0]?.role || '',
          contact_type: data.contact_details?.[0]?.is_primary ? 'primary' : 'secondary',
        };
        const defaultOption = titleOptions.find((option) => option.value === data.contact_details?.[0]?.title) || titleOptions[1];
        setDefaultValue(defaultOption);
        setFormData(formattedData);
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

  useEffect(() => {
    console.log('formData', formData);
  }, [formData]);

  async function onSubmit() {
    clearError(form.partner.update);
    setIsFormProcessing(true);

    let responseData;
    let docData;

    try {
      if (resource) {
        docData = await handleFileUpload(resource, 'partner', 'core/partner');
        responseData = await updatePartner(editId, { ...formData, logo: docData?.key || formData.logo });
      } else {
        responseData = await updatePartner(editId, formData);
      }

      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.partner.update, tBe);
      }

      if (responseData.is_success) {
        if (deletableResource) {
          const deleteResponse = await fileRemover(deletableResource);
          if (deleteResponse.success) {
            setDeletableResource(null);
          }
        }
        onCancel();
        afterEdit();
        setFormData(initCPartner);
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      setIsFormProcessing(false);
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen} size="xl" scrollable>
      <ModalHeader title={t('edit_entity', { entity: t('partner') })} onClose={() => onCancel()} />
      <ModalBody>
        <div id={`${form.partner.update}`}>
          {/* Basic Information Section */}
          <div className="row mb-4">
            <div className="col-12 col-md-12 col-lg-2 mb-2">
              <Label htmlFor="logo" label={t('logo')} />
              {skeleton ? (
                <Skeleton width="10rem" height="10rem" />
              ) : (
                <LogoUploader
                  width={140}
                  height={130}
                  cropShape={'rect'}
                  initialUrl={formData.logo ? `${process.env.S3CDN}/${formData.logo}` : undefined}
                  onChange={(selectedFiles: any) => {
                    setResource(selectedFiles);
                  }}
                />
              )}
            </div>
            <div className="col-12 col-md-10">
              <div className="row">
                <div className="col-12 col-md-4 mb-2">
                  <Label label={t('partner_name')} isRequired />
                  {skeleton ? <InputSkeleton /> : <Input value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />}
                </div>
                <div className="col-12 col-md-4 mb-2">
                  <Label label={t('email')} isRequired />
                  {skeleton ? <InputSkeleton /> : <Input value={formData.email} onChange={(e) => onFormChange('email', e.target.value)} className="form-control error-email" name="email" />}
                </div>
                <div className="col-12 col-md-4 mb-2">
                  <Label label={t('contact_number')} isRequired />
                  {skeleton ? (
                    <InputSkeleton />
                  ) : (
                    <ReactPhoneInput
                      value={formData.contact_number}
                      onChange={(phone) => onFormChange('contact_number', phone)}
                      defaultCountryCode={'lk'}
                      enableAreaCodes={false}
                      className="form-control error-contact_number"
                    />
                  )}
                </div>
                <div className="col-12 col-md-4 mb-2">
                  <Label label={t('fax_number')} />
                  {skeleton ? (
                    <InputSkeleton />
                  ) : (
                    <Input value={formData.fax_no} type="number" onChange={(e) => onFormChange('fax_no', e.target.value)} className="form-control error-fax_no" name="fax_no" />
                  )}
                </div>
                <div className="col-12 col-md-4 mb-2">
                  <Label label={t('address')} isRequired />
                  {skeleton ? <InputSkeleton /> : <Input value={formData.address} onChange={(e) => onFormChange('address', e.target.value)} className="form-control error-address" name="address" />}
                </div>
                <div className="col-12 col-md-4 mb-2">
                  <Label label={t('website')} />
                  {skeleton ? <InputSkeleton /> : <Input value={formData.website} onChange={(e) => onFormChange('website', e.target.value)} className="form-control error-website" name="website" />}
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
              {skeleton ? (
                <InputSkeleton />
              ) : (
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
                  className="form-control error-contact_title p-0"
                  defaultValue={{ label: formData.contact_type.charAt(0).toUpperCase() + formData.contact_type.slice(1), value: formData.contact_type }}
                />
              )}
            </div>
            <div className="col-12 col-md-4 mb-2">
              <Label label={t('salutation')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Select
                  defaultValue={defaultValue}
                  onChange={(value) => onFormChange('contact_title', value)}
                  options={titleOptions}
                  option={{ label: 'label', value: 'value' }}
                  isSearchable={false}
                  className="form-control error-contact_title p-0"
                />
              )}
            </div>
            <div className="col-12 col-md-4 mb-2">
              <Label label={t('contact_person_name')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input value={formData.contact_name} onChange={(e) => onFormChange('contact_name', e.target.value)} className="form-control error-contact_name" name="contact_name" />
              )}
            </div>
            <div className="col-12 col-md-4 mb-2">
              <Label label={t('role')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input value={formData.contact_role} onChange={(e) => onFormChange('contact_role', e.target.value)} className="form-control error-contact_role" name="contact_role" />
              )}
            </div>
          </div>

          <div className="row">
            <div className="col-12 col-md-4 mb-2">
              <Label label={t('email')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input value={formData.contact_email} onChange={(e) => onFormChange('contact_email', e.target.value)} className="form-control error-contact_email" name="contact_email" />
              )}
            </div>
            <div className="col-12 col-md-4 mb-2">
              <Label label={t('contact_number')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <ReactPhoneInput
                  value={formData.contact_primary}
                  onChange={(phone) => onFormChange('contact_primary', phone)}
                  defaultCountryCode={'lk'}
                  enableAreaCodes={false}
                  className="form-control error-contact_primary"
                />
              )}
            </div>
            <div className="col-12 col-md-4 mb-2">
              <Label label={t('remarks')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  type="textarea"
                  value={formData.contact_remarks}
                  onChange={(e) => onFormChange('contact_remarks', e.target.value)}
                  className="form-control error-contact_remarks"
                  name="contact_remarks"
                />
              )}
            </div>
          </div>

          {/* Bank Account Information Section */}
          <div className="row">
            <div className="col-12">
              <div className="panel-title mb-2">{t('bank_account_info')}</div>
            </div>
            <div className="col-12 col-md-4 mb-2">
              <Label label={t('account_holder_name')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.account_holder_name}
                  onChange={(e) => onFormChange('account_holder_name', e.target.value)}
                  className="form-control error-account_holder_name"
                  name="account_holder_name"
                />
              )}
            </div>
            <div className="col-12 col-md-4 mb-2">
              <Label label={t('bank_name')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input value={formData.bank_name} onChange={(e) => onFormChange('bank_name', e.target.value)} className="form-control error-bank_name" name="bank_name" />
              )}
            </div>
            <div className="col-12 col-md-4 mb-2">
              <Label label={t('account_number')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  type="text"
                  value={formData.account_number}
                  onChange={(e) => {
                    onFormChange('account_number', e.target.value);
                  }}
                  className="form-control error-account_number"
                  name="account_number"
                />
              )}
            </div>
          </div>

          <div className="row mb-4">
            <div className="col-12 col-md-4 mb-2">
              <Label label={t('bank_branch')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input value={formData.bank_branch} onChange={(e) => onFormChange('bank_branch', e.target.value)} className="form-control error-bank_branch" name="bank_branch" />
              )}
            </div>
            <div className="col-12 col-md-4 mb-2">
              <Label label={t('isbn_swift_code')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.iban_swift_code}
                  type="number"
                  onChange={(e) => onFormChange('iban_swift_code', e.target.value)}
                  className="form-control error-iban_swift_code"
                  name="iban_swift_code"
                />
              )}
            </div>
            <div className="col-12 col-md-4 mb-2">
              <Label label={t('payment_gateway_url')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.payment_gateway_url}
                  onChange={(e) => onFormChange('payment_gateway_url', e.target.value)}
                  className="form-control error-payment_gateway_url"
                  name="payment_gateway_url"
                />
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
