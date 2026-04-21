import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { IFormData, IrevisedData } from '../_utils/model';
import { thousandSeparator } from '@/helpers/services/commonService';

function RevisedCommission({
  isOpen,
  onCancel,
  uiFormData,
  currentTeamId,
  currentTeamMemberId,
  isFormProcessing,
  formData,
  setFormData,
  currentIProductId,
  setTeamUserTableVers,
}: {
  isOpen: boolean;
  onCancel: Function;
  uiFormData: IFormData;
  currentTeamMemberId: string;
  currentTeamId: string;
  isFormProcessing?: boolean;
  formData: IFormData[];
  setFormData: Function;
  currentIProductId: string;
  setTeamUserTableVers: Function;
}) {
  const t = useTrans('label.commission_setup,otr.common');
  const [rCommisionValue, setRCommisionValue] = useState('');

  useEffect(() => {
    if (isOpen) {
      // Find the current product data
      const currentProduct = formData.find((product) => product.id === currentIProductId);

      if (currentProduct) {
        // Find the latest revised commission for this team/user
        const latestRevision = currentProduct.revised_commission_percent?.find((rev) => rev.team_id === currentTeamId && rev.user_id === currentTeamMemberId);

        // Set initial value if found, otherwise use the default from props
        setRCommisionValue(latestRevision?.value || '');
      }
    }
  }, [isOpen, formData, currentIProductId, currentTeamId, currentTeamMemberId]);

  const handleSaveRCommision = () => {
    if (!rCommisionValue) {
      return;
    }

    const newRevisedEntry: IrevisedData = {
      team_id: currentTeamId,
      user_id: currentTeamMemberId,
      value: rCommisionValue,
      type: uiFormData.commission_type,
    };

    setFormData((prevFormData: IFormData[]) => {
      return prevFormData.map((product) => {
        if (product.id === currentIProductId) {
          const existingRevised = product.revised_commission_percent || [];

          // Check if an entry with the same team_id and user_id already exists
          const existingIndex = existingRevised.findIndex((entry) => entry.team_id === currentTeamId && entry.user_id === currentTeamMemberId);

          if (existingIndex >= 0) {
            // Update existing entry
            const updatedRevised = [...existingRevised];
            updatedRevised[existingIndex] = newRevisedEntry;
            return {
              ...product,
              revised_commission_percent: updatedRevised,
            };
          } else {
            // Add new entry
            return {
              ...product,
              revised_commission_percent: [...existingRevised, newRevisedEntry],
            };
          }
        }
        return product;
      });
    });
    setTeamUserTableVers((prev: any) => prev + 1);
    onCancel();
  };

  return (
    <Modal isOpen={isOpen} onBackdrop={() => onCancel()}>
      <ModalHeader title={t('edit_revised_commission')} onClose={() => onCancel()} />
      <ModalBody>
        <div className="row">
          {/* Brokerage Commission Section */}
          <div className="col-12 my-3">
            <div className="row">
              <div className="col-12 col-md-6 mb-3">
                <Label htmlFor="brokerage_commission_type" label={t('commission_type')} />
                <div className="mb-3 d-flex flex-row gap-2 align-items-center">
                  <input type="radio" id="r_fixed" name="r_percentage_method" value="fixed" className="mb-2" checked={uiFormData?.brokerage_commission_type === 'fixed'} disabled />
                  <Label htmlFor="r_fixed" label={t('fixed')} />
                  <input type="radio" id="r_percentage" name="r_percentage_method" value="percentage" className="mb-2" checked={uiFormData?.brokerage_commission_type === 'percentage'} disabled />
                  <Label htmlFor="r_percentage" label={t('percentage')} />
                </div>
              </div>
              <div className="col-12 col-md-6">
                <Input
                  label={t('brokerage_revenue')}
                  value={thousandSeparator(uiFormData?.brokerage_commission_value)}
                  className="form-control error-brokerage_commission_value"
                  name="brokerage_commission_value"
                  type="text"
                  disabled
                />
              </div>
            </div>
          </div>

          {/* Agent Commission Section */}
          <div className="col-12 my-3">
            <div className="row">
              <div className="col-12 col-md-6 mb-3">
                <Label htmlFor="commission_type" label={t('commission_type')} />
                <div className="mb-3 d-flex flex-row gap-2 align-items-center">
                  <input type="radio" id="r_a_fixed" name="r_a_percentage_method" value="fixed" className="mb-2" disabled checked={uiFormData?.commission_type === 'fixed'} />
                  <Label htmlFor="a_fixed" label={t('fixed')} />
                  <input type="radio" id="r_a_percentage" name="r_a_percentage_method" value="percentage" className="mb-2" checked={uiFormData?.commission_type === 'percentage'} disabled />
                  <Label htmlFor="r_a_percentage" label={t('percentage')} />
                </div>
              </div>
              <div className="col-12 col-md-6">
                <Input
                  label={t('agent_commission')}
                  value={thousandSeparator(uiFormData?.commission_value)}
                  className="form-control error-commission_value"
                  name="commission_value"
                  type="text"
                  disabled
                />
              </div>
            </div>
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

export default RevisedCommission;
