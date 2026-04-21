import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { FormEvent, useEffect, useState } from 'react';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { useTrans } from '@/helpers/services/lang/langService';
import { initFormDataAssignedTask } from '../../model';
import { getOneAssignedTask, getOneTaskStatus, getOneUser, updateAssignedTask } from '../../api-service';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllAssigneesDropdownData, fetchAllTaskStatuses } from '../../service';

export const EditAssignedTask = ({ isOpen, editId, afterUpdate, onCancel }: { isOpen: boolean; editId: string; onCancel: Function; afterUpdate: Function }) => {
  const t = useTrans('label.tasks,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState<any>(initFormDataAssignedTask);
  const [skeleton, setSkeleton] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneAssignedTask(editId);

      if (responseData?.is_success) {
        const data = responseData.result;
        setFormData(data);
        const assignedId = responseData.result.assigned_to_id;
        const taskStatusId = responseData.result.task_status_id;
        if (assignedId) {
          const response = await getOneUser(assignedId);
          if (response.is_success) {
            onFormChange('assigned_user', response.result.display_name);
          }
        }

        if (taskStatusId) {
          const response = await getOneTaskStatus(taskStatusId);
          if (response.is_success) {
            const tasks = response.result.find((task: any) => task.id === taskStatusId);
            onFormChange('task_status', tasks.name);
          }
        }

        // onFormChange('task', data.task);
        // onFormChange('task_status_id', data.task_status_id);
        // onFormChange('description', data.description);
        // onFormChange('assigned_to_id', data.assigned_to_id);
        // onFormChange('assigned_date', data.assigned_date);
        // onFormChange('start_date', data.start_date);
        // onFormChange('due_date', data.due_date);
        setSkeleton(false);
      }
    };

    if (editId) {
      setSkeleton(true);
      fetchData();
    }
  }, [editId]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.assigned_task.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updateAssignedTask(editId, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.assigned_task.update, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        onCancel();
        afterUpdate();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('edit_task_details')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.assigned_task.update}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              <Label label={t('task')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input type="textarea" value={formData.task || ''} onChange={(e) => onFormChange('task', e.target.value)} className="form-control error-task" name="task" />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label htmlFor="task_status" label={t('task_status')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <AsyncSelect
                  onChange={(_value: any, data: any) => {
                    onFormChange('task_status_id', data.id);
                    onFormChange('task_status', data.name);
                  }}
                  className="error-task_status_id"
                  loadOptions={fetchAllTaskStatuses}
                  option={{
                    label: 'name',
                    value: 'id',
                  }}
                  defaultValue={{
                    id: formData.task_status_id,
                    name: formData.task_status,
                  }}
                />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label htmlFor="assigned_to_id" label={t('assigned_to')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
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
                  defaultValue={{
                    id: formData.assigned_to_id,
                    display_name: formData.assigned_user,
                  }}
                />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('assigned_date')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.assigned_date || ''}
                  onChange={(e) => onFormChange('assigned_date', e.target.value)}
                  className="form-control error-assigned_date"
                  id="assigned_date"
                  name="assigned_date"
                  type="date"
                />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('start_date')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.start_date || ''}
                  onChange={(e) => onFormChange('start_date', e.target.value)}
                  className="form-control error-start_date"
                  id="start_date"
                  name="start_date"
                  type="date"
                />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('due_date')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input value={formData.due_date || ''} onChange={(e) => onFormChange('due_date', e.target.value)} className="form-control error-due_date" id="due_date" name="due_date" type="date" />
              )}
            </div>
            <div className="col-12 mb-3">
              <Label label={t('description')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input type="textarea" value={formData.description || ''} onChange={(e) => onFormChange('description', e.target.value)} className="form-control error-description" name="description" />
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
