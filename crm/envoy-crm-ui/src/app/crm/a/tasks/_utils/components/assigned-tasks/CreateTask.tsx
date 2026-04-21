import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useEffect, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { createAssignedTask } from '../../api-service';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { initFormDataAssignedTask } from '../../model';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllAssigneesDropdownData, fetchAllOpportunities, fetchAllTaskStatuses } from '../../service';
import { hexToRgba } from '@/helpers/services/commonService';

function CreateTask({ isOpen, onCancel, afterSave, opData }: { isOpen: boolean; onCancel: Function; afterSave: Function; opData?: any }) {
  const t = useTrans('label.tasks,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormDataAssignedTask);
  const [defaultLead, setDefaultLead] = useState({});

  useEffect(() => {
    if (opData) {
      onFormChange('opportunity_id', opData.id);
    }
    opData && setDefaultLead(opData);
  }, [opData]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.assigned_task.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createAssignedTask(formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.assigned_task.store, tBe);
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
      <ModalHeader title={t('create_new_entity', { entity: t('task') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.assigned_task.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              <Input label={t('task')} type="textarea" isRequired value={formData.task} onChange={(e) => onFormChange('task', e.target.value)} className="form-control error-task" name="task" />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="lead" label={t('lead')} isRequired />
              <AsyncSelect
                defaultValue={defaultLead}
                onChange={(value) => {
                  onFormChange('opportunity_id', value);
                }}
                loadOptions={(searchValue: any, currentPage: any) => fetchAllOpportunities(searchValue, currentPage)}
                option={{
                  labelFn: (option) => (
                    <>
                      <div className="text">{option.title}</div>
                      <div className="d-flex align-items-center gap-2 mt-1">
                        <div
                          className={'rounded-5 fw-semibold badge error-lead_id'}
                          style={{ background: hexToRgba(option.stage_color, 0.1), border: `1px solid ${hexToRgba(option.stage_color, 0.4)}`, color: option.stage_color }}
                        >
                          {option.stage_name}
                        </div>
                        <div className="text-muted">|</div>
                        <div className="text">{option.code}</div>
                      </div>
                    </>
                  ),
                  label: 'title',
                  value: 'id',
                }}
                className="form-control error-opportunity_id"
              />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="task_status" label={t('task_status')} isRequired />
              <AsyncSelect onChange={(value: any) => onFormChange('task_status_id', value)} className="form-control error-task_status_id" loadOptions={fetchAllTaskStatuses} />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="assigned_to_id" label={t('assigned_to')} />
              <AsyncSelect
                onChange={(_value: any, data: any) => {
                  onFormChange('assigned_to_id', data.id);
                  onFormChange('assigned_user', data.display_name);
                }}
                className="error-assigned_to_id"
                loadOptions={fetchAllAssigneesDropdownData}
                option={{
                  label: 'display_name',
                  value: 'id',
                }}
              />
            </div>

            <div className="col-12 col-md-6 mb-3">
              <Input
                label={t('assigned_date')}
                value={formData.assigned_date}
                onChange={(e) => onFormChange('assigned_date', e.target.value)}
                className="form-control error-assigned_date"
                name="assigned_date"
                type="date"
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                label={t('start_date')}
                value={formData.start_date}
                onChange={(e) => onFormChange('start_date', e.target.value)}
                className="form-control error-start_date"
                name="start_date"
                type="date"
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input label={t('due_date')} value={formData.due_date} onChange={(e) => onFormChange('due_date', e.target.value)} className="form-control error-due_date" name="due_date" type="date" />
            </div>
          </div>
          <div className="col-12 mb-3">
            <Input
              type="textarea"
              label={t('description')}
              value={formData.description}
              onChange={(e) => onFormChange('description', e.target.value)}
              className="form-control error-description"
              name="description"
            />
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

export default CreateTask;
