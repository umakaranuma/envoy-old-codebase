import { form } from '@/constans/Form';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Select } from '@apptimus-ui/select';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { MODULES } from '../service';
import { createReportType } from '../api-service';
import { toaster } from '@/helpers/services/toaster';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';

function CreateReportType({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: () => void; afterSave: () => void }) {
  const t = useTrans('label.report_type,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [formData, setFormData] = useState({ name: '', module: '', description: '' });
  const [isFormProcessing, setIsFormProcessing] = useState(false);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.report_type.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createReportType(formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.report_type.store, tBe);
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
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('create_new_report_type')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.report_type.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Input isRequired label={t('name')} value={formData.name} onChange={(e) => onFormChange('name', e.target.value)} className="form-control error-name" name="name" />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="form" label={t('report_type')} isRequired />
              <Select
                onChange={(value) => onFormChange('module', value)}
                className="form-control error-module"
                option={{
                  value: 'value',
                  label: 'label',
                }}
                options={MODULES}
                allowClear
              />
            </div>
            <div className="col-12 mb-3">
              <Input
                type="textarea"
                label={t('description')}
                rows={3}
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
            <Button text={t('save')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default CreateReportType;
