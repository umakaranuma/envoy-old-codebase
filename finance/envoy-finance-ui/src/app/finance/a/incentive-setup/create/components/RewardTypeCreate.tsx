import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { useEffect, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';

export const RewardTypeCreate = ({ isOpen, position, intidata, onSave, onCancel }: { isOpen: boolean; position: number[] | null; intidata: any; onCancel: Function; onSave: Function }) => {
  const t = useTrans('label.incentive_setup,otr.common');
  const [formData, setFormData] = useState<any>(intidata || { reward_type: 'fixed', reward_type_value: '' });

  useEffect(() => {
    console.log('intidata', intidata);

    setFormData(intidata || { reward_type: 'fixed', reward_type_value: '' });
  }, [intidata]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    onSave(formData, position);
    setFormData(null);
  }

  return (
    <Modal isOpen={isOpen} onBackdrop={() => onCancel()}>
      <ModalHeader title={t('add_reward_type')} onClose={() => onCancel()} />
      <form>
        <ModalBody>
          <>
            <div className="row">
              <div className="col-12 col-md-6 mb-3">
                <Label htmlFor="reward_type" label={t('reward_type')} isRequired />
                <div className="mb-3 d-flex flex-row gap-2 align-items-center">
                  <input
                    type="radio"
                    id="fixed"
                    name="reward_type"
                    value="fixed"
                    className="mb-2"
                    onChange={(e) => onFormChange('reward_type', e.target.value)}
                    checked={formData?.reward_type === 'fixed'}
                  />
                  <Label htmlFor="fixed" label={t('fixed')} />
                  <input
                    type="radio"
                    id="percentage"
                    name="reward_type"
                    value="percentage"
                    className="mb-2"
                    onChange={(e) => onFormChange('reward_type', e.target.value)}
                    checked={formData?.reward_type === 'percentage'}
                  />
                  <Label htmlFor="percentage" label={t('percentage')} />
                </div>
              </div>
              <div className="col-12 col-md-6 mb-3">
                <Input
                  label={t('reward_type_value')}
                  value={formData?.reward_type_value}
                  onChange={(e) => onFormChange('reward_type_value', e.target.value)}
                  className="form-control"
                  name="reward_type_value"
                  type="number"
                  isRequired
                />
              </div>
            </div>
          </>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('save')} type="button" width="sm" onClick={onSubmit} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
};
