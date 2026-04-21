import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label, Skeleton } from '@apptimus-ui/ui-element';
import React, { FormEvent, useEffect, useState } from 'react';
import { getOneUser, updateUser } from '../api-service';
import { IDisplayName, initUserData, IUser } from '../model';
import { AsyncSelect, Select } from '@apptimus-ui/select';
import { getAllRoles } from '../service';
import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import ReactPhoneInput from '@/components/others/page-related/ReactPhoneInput';

function Edit({ isOpen, onCancel, viewId, afterSave }: { viewId: string; isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const t = useTrans('label.user,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [data, setData] = useState<IUser>(initUserData);
  const [skeleton, setSkeleton] = useState(true);
  const [displayNames, setDisplayNames] = useState<IDisplayName[]>([]);
  const [isFormProcessing, setIsFormProcessing] = useState(false);

  const generateDisplayName = () => {
    const nameCollection = [
      { label: data.title + ' ' + data.first_name + ' ' + data.last_name },
      { label: data.last_name + ' ' + data.first_name },
      { label: data.first_name + ', ' + data.last_name },
    ];
    setDisplayNames(nameCollection);
  };

  useEffect(() => {
    generateDisplayName();
  }, [data.title, data.first_name, data.last_name]);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneUser(viewId);
      responseData?.is_success && (setData({ ...responseData.result, title: responseData.result.title || '' }), setSkeleton(false));
    };

    if (viewId) {
      setSkeleton(true);
      fetchData();
    }
  }, [viewId]);

  const onFormChange = (name: string, value: any) => {
    setData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.user_invite.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updateUser(viewId, data);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.user_invite.update, tBe);
      }

      if (responseData.is_success) {
        afterSave();
        onCancel();
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen} size="lg">
      <ModalHeader title={t('user_staff')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.user_invite.update}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('salutation')} isRequired />
              {skeleton ? (
                <Skeleton height="40px" />
              ) : (
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
                  defaultValue={{ label: data.title, value: data.title }}
                  className="form-control error-title p-0"
                />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('first_name')} />
              {skeleton ? (
                <Skeleton height="40px" />
              ) : (
                <Input isRequired value={data.first_name || ''} onChange={(e) => onFormChange('first_name', e.target.value)} className="form-control error-first_name" name="first_name" />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('last_name')} />
              {skeleton ? (
                <Skeleton height="40px" />
              ) : (
                <Input value={data.last_name || ''} onChange={(e) => onFormChange('last_name', e.target.value)} className="form-control error-last_name" name="last_name" />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('display_name')} isRequired />
              {skeleton ? (
                <Skeleton height="40px" />
              ) : (
                <Select
                  onChange={(value) => onFormChange('display_name', value)}
                  options={displayNames}
                  option={{ label: 'label', value: 'label' }}
                  isSearchable={false}
                  defaultValue={{ label: data.display_name, value: data.display_name }}
                />
              )}
            </div>
            {/* <div className="col-12 col-md-6 mb-3">
              <Label label={t('email')} isRequired />
              {skeleton ? <Skeleton height="40px" /> : <Input value={data.email || ''} onChange={(e) => onFormChange('email', e.target.value)} className="form-control error-email" name="email" />}
            </div> */}
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('contact_number')} />
              {skeleton ? (
                <Skeleton height="40px" />
              ) : (
                // <PhoneInput
                //   country={'lk'}
                //   enableAreaCodes={true}
                //   value={data.contact_no?.toString()}
                //   inputStyle={{ height: '40px', width: '100%' }}
                //   containerStyle={{ height: '40px', width: '100%' }}
                //   onChange={(phone) => {
                //     if (phone.replace(/\D/g, '').length <= 15) {
                //       onFormChange('contact_no', phone);
                //     }
                //   }}
                //   countryCodeEditable={false}
                // />
                <ReactPhoneInput
                  value={data.contact_no?.toString() || ''}
                  onChange={(phone) => onFormChange('contact_no', phone)}
                  defaultCountryCode={'lk'}
                  enableAreaCodes={false}
                  className="form-control error-contact_no"
                />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('user_role')} isRequired />
              {skeleton ? (
                <Skeleton height="40px" />
              ) : (
                <AsyncSelect
                  className="error-role_id"
                  onChange={(_value: any, data: any) => {
                    onFormChange('role_id', data.id);
                    onFormChange('role_name', data.name);
                  }}
                  option={{
                    label: 'name',
                    value: 'id',
                  }}
                  defaultValue={{
                    name: data.role_name,
                    id: data.role_id,
                  }}
                  loadOptions={(searchValue, currentPage) => getAllRoles(searchValue, currentPage)}
                />
                // <AsyncSelect
                //   onChange={(value: any) => onFormChange('role_id', value)}
                //   className="error-assigned_to_id"
                //   loadOptions={fetchAllAssigneesDropdownData}
                //   option={{
                //     label: 'display_name',
                //   }}
                // />
              )}
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button type="submit" text={t('update')} color="primary" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default Edit;
