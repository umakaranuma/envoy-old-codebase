'use client';
import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { createPanel, createStep, createTemplate } from '../api-service';
import { initFormData } from '../model';
import { Select } from '@apptimus-ui/select';
import { defaulttemplateType, templateTypeOptions } from '../constant';
import { useRouter } from 'next/navigation';

function TemplatesCreate({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const t = useTrans('label.template,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initFormData);
  const router = useRouter();

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };
  async function createDefaultStepsAndPanels(templateId: string, templateType: string) {
    try {
      // Create first step (always created)

      // For 'single' type, only create one step and one panel
      if (templateType === 'single_form') {
        const panel1 = await createPanel({ title: 'Untitled Panel', step_id: '' }, templateId);
        return {
          panels: [panel1],
        };
      }

      // For multi_step_form types, create second step and both panels
      const step1 = await createStep({ title: 'Step 1', order_number: 1 }, templateId);
      const step2 = await createStep({ title: 'Step 2', order_number: 2 }, templateId);

      const [panel1, panel2] = await Promise.all([
        createPanel({ title: 'Untitled Panel', step_id: step1.result.id }, templateId),
        createPanel({ title: 'Untitled Panel', step_id: step2.result.id }, templateId),
      ]);

      return {
        steps: [step1, step2],
        panels: [panel1, panel2],
      };
    } catch (error) {
      console.error('Error creating default steps and panels:', error);
      throw error;
    }
  }

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.forms.store);
    setIsFormProcessing(true);

    try {
      const templateResponse = await createTemplate(formData);

      if (templateResponse.status_code === 417) {
        printError(templateResponse.result, form.forms.store, tBe);
        return;
      }

      if (templateResponse.is_success) {
        // Create default step and panel after successful template creation
        await createDefaultStepsAndPanels(templateResponse.result.id, templateResponse.result.type);

        toaster.success(tBe(templateResponse.message));
        setFormData(initFormData);
        afterSave();
        router.push(`/a/templates/${templateResponse.result.id}`);
      }
    } catch (error) {
      console.error('Template creation failed:', error);
      toaster.error(tBe('creation_failed'));
    } finally {
      setIsFormProcessing(false);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('create_new_template', { entity: t('form') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.forms.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Input isRequired label={t('title')} value={formData.title} onChange={(e) => onFormChange('title', e.target.value)} className="form-control error-title" name="title" />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Label label={t('type')} isRequired />
              <Select
                onChange={(value, option) => {
                  onFormChange('type', value), console.log(option);
                }}
                options={templateTypeOptions}
                option={{
                  label: 'label',
                  value: 'id',
                  keysToSearch: ['type', 'id'],
                }}
                defaultValue={defaulttemplateType}
              />
            </div>
            <div className="col-12 mb-3">
              <Input
                type="textarea"
                label={t('description')}
                value={formData.description}
                onChange={(e) => onFormChange('description', e.target.value)}
                className="form-control error-description"
                name="description"
                rows={3}
              />
            </div>
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('save')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default TemplatesCreate;
