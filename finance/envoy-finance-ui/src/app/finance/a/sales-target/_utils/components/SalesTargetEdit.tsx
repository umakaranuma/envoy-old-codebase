import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import { FormEvent, useEffect, useState } from 'react';
import { emptyTargetResult, ISalesTargetResult } from '../model';
import { InputSkeleton } from '@/components/others/InputSkeleton';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { getOneSalesTarget, updateSalesTarget } from '../api-service';

export const SalesTargetEdit = ({ isOpen, editId, afterUpdate, onCancel, activetab }: { isOpen: boolean; editId: string; onCancel: Function; afterUpdate: Function; activetab: string }) => {
  const t = useTrans('label.sales_target,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(emptyTargetResult);
  const [skeleton, setSkeleton] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const responseData = await getOneSalesTarget(editId, activetab);
        if (responseData?.is_success) {
          const data: ISalesTargetResult = responseData.result;
          setFormData(data);
          setSkeleton(false);
        }
      } catch (error) {
        console.error(error);
      }
    };

    if (editId) {
      fetchData();
    }
  }, [editId]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  function getMonthName(monthNumber: number) {
    const monthKeys = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'];

    if (monthNumber >= 1 && monthNumber <= 12) {
      return t(monthKeys[monthNumber - 1]);
    }

    return '';
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    clearError(form.sales_target.update);
    setIsFormProcessing(true);

    try {
      const responseData = await updateSalesTarget(editId, activetab, formData);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.sales_target.update, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setFormData(emptyTargetResult);
        afterUpdate();
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <Modal isOpen={isOpen} onBackdrop={() => onCancel()}>
      <ModalHeader title={t('edit_sales_target', { entity: t('sales_target') })} onClose={() => onCancel()} />
      <form onSubmit={onSubmit} id={`${form.sales_target.update}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Label htmlFor="agent_info" label={activetab === 'individual' ? t('agent_info') : t('team_name')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input value={activetab === 'individual' ? formData.agent_name : formData.team_name} className="form-control" id="agent_name" name="agent_name" disabled />
              )}
            </div>
            {formData.period_type === 'monthly' ? (
              <div className="col-12 col-md-6 mb-3">
                <Label htmlFor="target_period" label={t('target_period')} isRequired />
                {skeleton ? <InputSkeleton /> : <Input value={`${getMonthName(formData.month)} ${formData.year}`} className="form-control" id="target_period" name="target_period" disabled />}
              </div>
            ) : (
              <div className="col-12 col-md-6 mb-3">
                <Label htmlFor="target_period" label={t('target_period')} isRequired />
                {skeleton ? <InputSkeleton /> : <Input value={formData.year || ''} className="form-control" id="target_period" name="target_period" disabled />}
              </div>
            )}

            <div className="col-12 col-md-6 mb-3">
              <Label htmlFor="achieved" label={t('achieved')} isRequired />
              {skeleton ? <InputSkeleton /> : <Input value={formData?.achieved || '0'} className="form-control" id="achieved" name="achieved" disabled />}
            </div>
            <div className="col-12 col-md-6  mb-3">
              <Label htmlFor="target_amount" label={t('target_amount')} isRequired />
              {skeleton ? (
                <InputSkeleton />
              ) : (
                <Input
                  value={formData.target_amount || ''}
                  type="number"
                  onChange={(e) => onFormChange('target_amount', e.target.value)}
                  className="form-control error-target_amount"
                  id="target_amount"
                  name="target_amount"
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
