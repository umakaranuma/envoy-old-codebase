import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useEffect, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { toaster } from '@/helpers/services/toaster';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllTeamsDropdown } from '../../service';
import { addMemberInTeam } from '../../api-service';
import { initSingleTeamFormData } from '../../model';

function AddMemberInTeam({ isOpen, onCancel, afterSave, userId }: { isOpen: boolean; onCancel: Function; afterSave: Function; userId: string }) {
  const t = useTrans('label.user,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initSingleTeamFormData);
  const [teamId, setTeamId] = useState('');

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  };

  useEffect(() => {
    onFormChange('user_ids', [userId]);
  }, [userId]);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.job_title.store);
    setIsFormProcessing(true);

    try {
      const responseData = await addMemberInTeam(formData, teamId);
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
    <Modal isOpen={isOpen} onBackdrop={() => onCancel()} size="sm">
      <ModalHeader title={t('add_members_in_sales_team', { entity: t('job_title') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.job_title.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-12 mb-3 custom-select">
              <Label htmlFor="team" label={t('team')} isRequired />
              <AsyncSelect
                onChange={(_, data) => {
                  setTeamId(data.id);
                }}
                className="form-control error-name"
                option={{ label: 'name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => fetchAllTeamsDropdown(searchValue, currentPage)}
              />
            </div>
            {/* <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="sales_director" label={t('sales_director')} isRequired />
              <AsyncSelect
                onChange={(value) => onFormChange('detector_id', value)}
                className="form-control error-detector_id"
                option={{ label: 'display_name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => getAllUserDrpdown(searchValue, currentPage)}
              />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="sales_manager" label={t('sales_manager')} isRequired />
              <AsyncSelect
                onChange={(value) => onFormChange('manager_id', value)}
                className="form-control error-manager_id"
                option={{ label: 'display_name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => getAllUserDrpdown(searchValue, currentPage)}
              />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="sales_lead" label={t('sales_lead')} isRequired />
              <AsyncSelect
                onChange={(value) => onFormChange('leader_id', value)}
                className="form-control error-leader_id"
                option={{ label: 'display_name', value: 'id' }}
                isSearchable={true}
                loadOptions={(searchValue, currentPage) => getAllUserDrpdown(searchValue, currentPage)}
              />
            </div> */}
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('add')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default AddMemberInTeam;
