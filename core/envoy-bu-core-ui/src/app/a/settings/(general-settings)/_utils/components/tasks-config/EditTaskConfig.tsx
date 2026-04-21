import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { FormEvent, useEffect, useState } from 'react';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { useTrans } from '@/helpers/services/lang/langService';
import { printError } from '@/helpers/handlers/validationErrorHandler';
import { initFormData, ITaskConfigs } from '../../model';
import { getOneTaskConfigs, updateTaskConfigs } from '../../api-service';

export const EditTaskConfig = ({ isOpen, editId, afterUpdate, onCancel }: { isOpen: boolean; editId: string; onCancel: Function; afterUpdate: Function }) => {
  const t = useTrans('label.general_settings,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);
  const [skeleton, setSkeleton] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneTaskConfigs(editId);

      if (responseData?.is_success) {
        const data: ITaskConfigs = responseData.result;
        onFormChange('task_type_id', data.task_type_id);
        onFormChange('task', data.task);
        onFormChange('expected_days', data.expected_days);
        onFormChange('reminder_expected_days', data.reminder_expected_days);
        onFormChange('opportunity_status_id', data.opportunity_status_id);
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

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsFormProcessing(true);

    try {
      const responseData = await updateTaskConfigs(editId, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.task_config_type.update, tBe);
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
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('edit_task_details')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.task_config_type.update}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 mb-3">
              <Label label={t('task')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input isRequired value={formData.task || ''} onChange={(e) => onFormChange('task', e.target.value)} className="form-control error-task" id="task" name="task" type="textarea" />
              )}
            </div>
            {/* <div className="col-12 col-md-6 mb-3">
              <Label label={t('task_type')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input isRequired value={formData.task} onChange={(e) => onFormChange('task', e.target.value)} className="form-control error-task" id="task" name="task" />
              )}
            </div> */}
            {/* <div className="col-12 col-md-6 mb-3">
              <Label label={t('assigned_stage')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  isRequired
                  value={formData.expected_days}
                  onChange={(e) => onFormChange('expected_days', e.target.value)}
                  className="form-control error-expected_days"
                  id="expected_days"
                  name="expected_days"
                />
              )}
            </div> */}
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('expected_time_period_to_complete')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.expected_days || 1}
                  onChange={(e) => onFormChange('expected_days', e.target.value)}
                  className="form-control error-expected_days"
                  id="expected_days"
                  name="expected_days"
                  type="number"
                  min={1}
                />
              )}
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('expected_time_to_send_reminder')} />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.reminder_expected_days || 0}
                  onChange={(e) => onFormChange('reminder_expected_days', e.target.value)}
                  className="form-control error-reminder_expected_days"
                  id="reminder_expected_days"
                  name="reminder_expected_days"
                  type="number"
                  min={0}
                />
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
