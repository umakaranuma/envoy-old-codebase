import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { toaster } from '@/helpers/services/toaster';
import { AsyncSelect } from '@apptimus-ui/select';
import { initTeamFormData } from '../model';
import { createSalesTeam } from '../api-service';
import { getAllUserDrpdown } from '@/app/a/users/_utils/service';
import { fetchAllNativeProducts } from '../service';

function CreateTeam({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const t = useTrans('label.teams,otr.common');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initTeamFormData);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  };

  const tBe = useTrans('be.msg,be.error,be.attri');

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.job_title.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createSalesTeam(formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.job_title.store, tBe);
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
    <Modal isOpen={isOpen} onBackdrop={() => onCancel()} size="lg">
      <ModalHeader title={t('create')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.job_title.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Input isRequired label={t('team_name')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="native_product" label={t('native_product')} />
              <AsyncSelect
                onChange={(value) => onFormChange('product_ids', value)}
                className="form-control error-product_ids"
                option={{ label: 'name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllNativeProducts(searchValue, currentPage)}
                multiple
              />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="team_lead" label={t('team_lead')} isRequired />
              <AsyncSelect
                onChange={(value) => onFormChange('manager_id', value)}
                className="form-control error-manager_id"
                option={{ label: 'display_name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => getAllUserDrpdown(searchValue, currentPage)}
              />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="team_member" label={t('team_member')} isRequired />
              <AsyncSelect
                onChange={(value) => onFormChange('user_ids', value)}
                className="form-control error-user_ids"
                option={{ label: 'display_name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => getAllUserDrpdown(searchValue, currentPage)}
                multiple
              />
            </div>
            <div className="col-12 mb-3">
              <Input
                type="textarea"
                rows={3}
                label={t('description')}
                value={formData.description}
                onChange={(e) => onFormChange('description', e.target.value)}
                className="form-control error-description"
                name="description"
              />
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('create')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default CreateTeam;
