import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { UIFormData } from '../../_utils/model';
import { Description } from '@/components/others/Description';
import { formatCommissionValue } from '../../_utils/services';
import { getCurrency } from '@/helpers/services/currencyService';

function EditRevisedCommission({
  isOpen,
  onCancel,
  uiFormData,
  rCommisSionData,
  setRCommisSionData,
  currentTeamId,
  currentTeamMemberId,
  onEdit,
  isFormProcessing,
}: {
  isOpen: boolean;
  onCancel: Function;
  uiFormData: UIFormData;
  rCommisSionData: any;
  setRCommisSionData: any;
  currentTeamMemberId: string;
  currentTeamId: string;
  onEdit: Function;
  isFormProcessing?: boolean;
}) {
  const t = useTrans('label.commission_setup,otr.common');
  const [rCommisionValue, setRCommisionValue] = useState('');
  const currency = getCurrency();
  console.log('rCommisSionData', rCommisSionData);

  const formatValue = (value: number | string | undefined, type: string | undefined) => {
    return formatCommissionValue(value, type, currency.code);
  };

  useEffect(() => {
    const compositeKey = `${currentTeamId}_${currentTeamMemberId}`;
    const existingValue = rCommisSionData[compositeKey] || '';

    setRCommisionValue(existingValue);
  }, [isOpen]);

  const handleSaveRCommision = () => {
    const compositeKey = `${currentTeamId}_${currentTeamMemberId}`;
    const newData = {
      ...rCommisSionData,
      [compositeKey]: rCommisionValue || '',
    };
    console.log('newData', newData);

    setRCommisSionData(newData);
    onEdit(newData);
  };

  return (
    <Modal isOpen={isOpen} onBackdrop={() => onCancel()}>
      <ModalHeader title={t('add_revised_commission')} onClose={() => onCancel()} />
      <ModalBody>
        <div className="row">
          {/* Brokerage Commission Section */}
          {/* <div className="col-12 my-3">
            <div className="row">
              <div className="col-12 col-md-6 mb-3">
                <Label htmlFor="brokerage_commission_type" label={t('commission_type')} />
                <div className="mb-3 d-flex flex-row gap-2 align-items-center">
                  <input type="radio" id="r_fixed" name="r_percentage_method" value="fixed" className="mb-2" checked={uiFormData.brokerage_commission_type === 'fixed'} disabled />
                  <Label htmlFor="r_fixed" label={t('fixed')} />
                  <input type="radio" id="r_percentage" name="r_percentage_method" value="percentage" className="mb-2" checked={uiFormData.brokerage_commission_type === 'percentage'} disabled />
                  <Label htmlFor="r_percentage" label={t('percentage')} />
                </div>
              </div>
              <div className="col-12 col-md-6">
                <Input
                  label={t('brokerage_revenue')}
                  value={thousandSeparator(uiFormData.brokerage_commission_value) || ''}
                  className="form-control error-brokerage_commission_value"
                  name="brokerage_commission_value"
                  type="text"
                  disabled
                />
              </div>
            </div>
          </div> */}

          {/* Agent Commission Section */}
          {/* <div className="col-12 my-3">
            <div className="row">
              <div className="col-12 col-md-6 mb-3">
                <Label htmlFor="commission_type" label={t('commission_type')} />
                <div className="mb-3 d-flex flex-row gap-2 align-items-center">
                  <input type="radio" id="r_a_fixed" name="r_a_percentage_method" value="fixed" className="mb-2" disabled checked={uiFormData.commission_type === 'fixed'} />
                  <Label htmlFor="a_fixed" label={t('fixed')} />
                  <input type="radio" id="r_a_percentage" name="r_a_percentage_method" value="percentage" className="mb-2" checked={uiFormData.commission_type === 'percentage'} disabled />
                  <Label htmlFor="r_a_percentage" label={t('percentage')} />
                </div>
              </div>
              <div className="col-12 col-md-6">
                <Input
                  label={t('agent_commission')}
                  value={thousandSeparator(uiFormData.commission_value) || ''}
                  className="form-control error-commission_value"
                  name="commission_value"
                  type="text"
                  disabled
                />
              </div>
            </div>
          </div> */}

          <div className="col-6 my-3">
            <Description label={t('brokerage_commission')} value={formatValue(uiFormData.brokerage_commission_value, uiFormData.brokerage_commission_type)} />
          </div>
          <div className="col-6 my-3">
            <Description label={t('agent_commission')} value={formatValue(uiFormData.commission_value, uiFormData.commission_type)} />
          </div>
          <div className="col-6 mb-3">
            <Input
              value={rCommisionValue || ''}
              label={t('revised_commission_percentage')}
              onChange={(e) => setRCommisionValue(e.target.value)}
              className="form-control error-revised_commission_percentage"
              name="revised_commission_percentage"
              type="number"
            />
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('update')} type="button" width="sm" onClick={handleSaveRCommision} isLoading={isFormProcessing} />
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default EditRevisedCommission;
