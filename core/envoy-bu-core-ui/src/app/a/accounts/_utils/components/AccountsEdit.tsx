import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label, Skeleton } from '@apptimus-ui/ui-element';
import { FormEvent, useEffect, useState } from 'react';
import { initFormData, ICustomers } from '../model';
import { getOneCustomers, updateCustomers } from '../api-service';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { useTrans } from '@/helpers/services/lang/langService';
import { Select } from '@apptimus-ui/select';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { FlexField, useFlexField } from '@/components/others/FlexFiled';
import { getOneEntity } from '@/helpers/services/api-service';
import ReactPhoneInput from '@/components/others/page-related/ReactPhoneInput';

export const AccountsEdit = ({ isOpen, editId, afterUpdate, onCancel }: { isOpen: boolean; editId: string; onCancel: Function; afterUpdate: Function }) => {
  const t = useTrans('label.accounts,otr.common');
  const { fields } = useFlexField('CUSTOMER');
  fields.forEach((field) => (initFormData.flex_fields[field.id] = field.default_value || ''));
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);
  const [skeleton, setSkeleton] = useState(true);
  const [flexSkeleton, setFlexSkeleton] = useState(true);
  const [phoneVal, setPhoneVal] = useState('');

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

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneCustomers(editId);

      if (responseData?.is_success) {
        const data: ICustomers = responseData.result;

        if (data.entity_id) {
          setFlexSkeleton(true);
          const responseFlex = await getOneEntity(data.entity_id, 'flex_field_values');

          if (responseFlex?.is_success) {
            const responseFlexData = responseFlex.result.flex_field_values;
            const updatedFlexFields = { ...formData.flex_fields };
            Object.keys(updatedFlexFields).forEach((key) => {
              updatedFlexFields[key] = responseFlexData[key] || updatedFlexFields[key];
            });
            setFormData((prevFormData) => ({ ...prevFormData, flex_fields: updatedFlexFields }));
          }
        }
        setFlexSkeleton(false);
        onFormChange('type', data.type);
        onFormChange('name', data.name);
        onFormChange('code', data.code);
        onFormChange('email', data.primary_contact.email);
        onFormChange('address', data.primary_contact.address);
        onFormChange('website_url', data.primary_contact.website_url);
        onFormChange('primary_contact', data.primary_contact.primary_contact);
        onFormChange('secondary_contact', data.primary_contact.secondary_contact);
        onFormChange('remarks', data.remarks);
        setPhoneVal(data.primary_contact.primary_contact);
        setSkeleton(false);
      }
    };

    if (editId) {
      fetchData();
    }
  }, [editId]);

  const tBe = useTrans('be.msg,be.error,be.attri');
  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.customres_crud.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updateCustomers(editId, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.customres_crud.update, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setFormData(initFormData);
        afterUpdate();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen} size="lg">
      <ModalHeader title={t('edit_entity', { entity: t('account_details') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.customres_crud.update}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Label htmlFor="account_type" label={t('account_type')} isRequired />
              {skeleton ? (
                <Skeleton height="40px" />
              ) : (
                <Select
                  onChange={(value) => onFormChange('type', value)}
                  className="error-type"
                  options={[
                    { label: t('corporate'), value: 'Corporate' },
                    { label: t('personal'), value: 'Personal' },
                  ]}
                  option={{ label: 'label', value: 'value' }}
                  isSearchable={false}
                  defaultValue={{ label: formData.type, value: formData.type }}
                />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label htmlFor="account_name" label={t('account_name')} isRequired />
              {skeleton ? <InputSkeleton /> : <Input value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label htmlFor="email" label={t('email')} />
              {skeleton ? <InputSkeleton /> : <Input value={formData.email} onChange={(e) => onFormChange('email', e.target.value)} className="form-control error-email" name="email" />}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label htmlFor="address" label={t('address')} />
              {skeleton ? <InputSkeleton /> : <Input value={formData.address} onChange={(e) => onFormChange('address', e.target.value)} className="form-control error-address" name="address" />}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label htmlFor="website" label={t('website')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input type="url" value={formData.website_url} onChange={(e) => onFormChange('website_url', e.target.value)} className="form-control error-website_url" name="website_url" />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('primary_contact_number')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                // <PhoneInput
                //   country={'lk'}
                //   enableAreaCodes={true}
                //   value={phoneVal}
                //   inputStyle={{ height: '40px', width: '100%' }}
                //   containerStyle={{ height: '40px', width: '100%' }}
                //   onChange={(phone, data: import('react-phone-input-2').CountryData) => {
                //     if (phone === data?.dialCode) {
                //       onFormChange('primary_contact', '');
                //     } else {
                //       onFormChange('primary_contact', phone);
                //     }
                //   }}
                //   inputClass="form-control error-primary_contact"
                //   countryCodeEditable={false}
                // />
                <ReactPhoneInput
                  value={phoneVal}
                  onChange={(phone) => onFormChange('primary_contact', phone)}
                  defaultCountryCode={'lk'}
                  enableAreaCodes={false}
                  className="form-control error-primary_contact"
                />
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
                //   inputClass="form-control error-primary_contact_id"
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
            {fields.map((field, index) => (
              <div key={index} className="col-12 col-md-6 mb-3">
                <FlexField field={field} value={formData.flex_fields[field.id]} onChange={(name: string, value: any) => onFormChange(name, value, 'flex_fields')} skeleton={flexSkeleton} />
              </div>
            ))}
          </div>
          <div className="row">
            <div className="col-12 mb-3">
              <Label htmlFor="remarks" label={t('remarks')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input type="textarea" value={formData.remarks} onChange={(e) => onFormChange('remarks', e.target.value)} className="form-control error-remarks" name="remarks" />
              )}
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
