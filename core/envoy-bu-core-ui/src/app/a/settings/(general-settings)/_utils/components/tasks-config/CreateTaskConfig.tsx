import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { AsyncSelect } from '@apptimus-ui/select';
import { initFormData } from '../../model';
import { createTaskConfigs } from '../../api-service';
import { fetchAllOpportunityStages, fetchAllTaskTypes } from '../../service';

function CreateTaskConfig({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const t = useTrans('label.general_settings,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.task_config_type.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createTaskConfigs(formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.task_config_type.store, tBe);
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
    <Modal isOpen={isOpen} size="lg" onBackdrop={() => onCancel()}>
      <ModalHeader title={t('add_new_task_details')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.task_config_type.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              <Input label={t('task')} type="textarea" isRequired value={formData.task} onChange={(e) => onFormChange('task', e.target.value)} className="form-control error-task" name="task" />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="task_type" label={t('task_type')} isRequired />
              <AsyncSelect onChange={(value: any) => onFormChange('task_type_id', value)} className="" loadOptions={fetchAllTaskTypes} />
              <span className="error-task_type_id"></span>
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="assigned_stage" label={t('assigned_stage')} isRequired />
              <AsyncSelect onChange={(value: any) => onFormChange('opportunity_status_id', value)} className="" loadOptions={fetchAllOpportunityStages} />
              <span className="error-opportunity_status_id"></span>
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                type="number"
                label={`${t('expected_time_period_to_complete')} (${t('days')})`}
                value={formData.expected_days || 1}
                onChange={(e) => onFormChange('expected_days', e.target.value)}
                className="form-control error-expected_days"
                name="expected_days"
                min={1}
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                type="number"
                label={`${t('expected_time_to_send_reminder')} (${t('days')})`}
                value={formData.reminder_expected_days || 0}
                onChange={(e) => onFormChange('reminder_expected_days', e.target.value)}
                className="form-control error-reminder_expected_days"
                name="reminder_expected_days"
                min={0}
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

export default CreateTaskConfig;
