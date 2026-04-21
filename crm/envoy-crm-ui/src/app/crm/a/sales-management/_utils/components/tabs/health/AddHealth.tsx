import { form } from '@/constans/Form';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { FormEvent, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { addHealthOfOp } from '../../../api-service';
import { useParams } from 'next/navigation';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';

function AddHealth({ isOpen, onCancel, afterSave }: { isOpen: boolean; onCancel: Function; afterSave: Function }) {
  const t = useTrans('label.sales_managements,otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({ date: new Date().toISOString().split('T')[0], health: '' });
  const params = useParams();
  const managementId = params.managementId?.toString() || '';

  const healthCount = {
    0: '0',
    1: '1',
    2: '2',
    3: '3',
    4: '4',
    5: '5',
    6: '6',
    7: '7',
    8: '8',
    9: '9',
    10: '10',
  };
  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    clearError(form.assigned_task.store);
    setIsFormProcessing(true);

    try {
      const responseData = await addHealthOfOp(managementId, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.assigned_task.store, tBe);
      }

      if (responseData.is_success) {
        afterSave();
        //setFormData({ date: new Date().toISOString().split("T")[0], health: '' })
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('add_health')} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.assigned_task.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Input isRequired label={t('date')} value={formData.date} onChange={(e) => onFormChange('date', e.target.value)} className="form-control error-date" name="date" type="date" />
            </div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label htmlFor="health" label={t('health')} isRequired />
              {/* <Select
                onChange={(value) => onFormChange('health', value)}
                className="form-control error-health"
                option={{ label: 'label', value: 'value' }}
                isSearchable={false}
                options={healthCount}
              /> */}
              <Slider min={0} max={10} marks={healthCount} step={null} onChange={(value: any) => onFormChange('health', value)} defaultValue={0} trackStyle={[{ backgroundColor: '#088ab2' }]} />
            </div>
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

export default AddHealth;
