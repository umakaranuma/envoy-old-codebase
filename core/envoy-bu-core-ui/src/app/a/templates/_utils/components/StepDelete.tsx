import { form } from '@/constans/Form';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import 'react-phone-input-2/lib/style.css';
import { toaster } from '@/helpers/services/toaster';
import { deleteStep } from '../api-service';

function StepDelete({
  isOpen,
  onCancel,
  templateId,
  stepId,
  setSteps,
  activeStepId,
  setActiveStepId,
  afterDelete,
}: {
  isOpen: boolean;
  onCancel: Function;
  templateId: string;
  stepId: number;
  setSteps: any;
  activeStepId: any;
  setActiveStepId: any;
  afterDelete: any;
}) {
  const t = useTrans('label.template,otr.common');
  const [isLoading, setIsLoading] = useState(false);
  const tBe = useTrans('be.msg,be.error,be.attri');

  const handleDeleteStep = async (templateId: string, stepId: any) => {
    try {
      setIsLoading(true);
      const response = await deleteStep(templateId, stepId);

      if (response.is_success) {
        toaster.success(tBe(response.message));
        afterDelete();
        setSteps((prevSteps: any) => {
          const updatedSteps = prevSteps.filter((step: any) => step.id !== stepId);
          if (activeStepId === stepId) {
            setActiveStepId(updatedSteps[0]?.id || null);
          }
          return updatedSteps;
        });
      } else {
        toaster.error(tBe(response.message));
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} position="top">
      <ModalHeader title={t('delete_step')} onClose={() => onCancel()} />
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleDeleteStep(templateId, stepId);
        }}
        id={`${form.contact_crud.store}`}
      >
        <ModalBody>
          <div className="text-center">{t(`do_you_want_to_delete_this_record`)}</div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('delete')} type="submit" width="sm" isLoading={isLoading} color="danger" />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default StepDelete;
