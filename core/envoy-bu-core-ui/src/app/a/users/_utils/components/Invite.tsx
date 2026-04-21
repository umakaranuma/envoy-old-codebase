import { form } from '@/constans/Form';
import { useTrans } from '@/helpers/services/lang/langService';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { AsyncSelect } from '@apptimus-ui/select';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { initInviteUserForm } from '../model';
import { inviteUser } from '../api-service';
import { getAllRoles } from '../service';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';

function Invite({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const t = useTrans('label.user,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initInviteUserForm);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.user_invite.store);
    setIsFormProcessing(true);

    try {
      const responseData = await inviteUser(formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.user_invite.store, tBe);
      }

      if (responseData.is_success) {
        afterSave();
        setFormData(initInviteUserForm);
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('invite_user')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.user_invite.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-12 mb-3">
              <Input label={t('name')} isRequired value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-12 mb-3">
              <Label label={t('role')} isRequired />
              <div className="custom-select">
                <AsyncSelect
                  className="form-control error-role_id"
                  placeholder={t('select_role')}
                  onChange={(value: any) => {
                    onFormChange('role_id', value);
                  }}
                  option={{
                    label: 'name',
                    value: 'id',
                  }}
                  loadOptions={(searchValue, currentPage) => getAllRoles(searchValue, currentPage)}
                />
              </div>
            </div>
            <div className="col-12 col-md-12 mb-3">
              <Input
                isRequired
                label={t('email_address')}
                placeholder={t('user_email')}
                value={formData.email}
                onChange={(e) => onFormChange('email', e.target.value)}
                className="form-control error-email"
                name="email"
              />
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button type="submit" text={t('send')} color="primary" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default Invite;
