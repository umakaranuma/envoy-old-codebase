import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { IFormData } from '../_utils/model';
import { AsyncSelect } from '@apptimus-ui/select';
import { fetchAllTransationTypeData } from '../_utils/services';
import toast from 'react-hot-toast';

function AddCommison({
  isOpen,
  onCancel,
  currentIProductId,
  initialData,
  setFormData,
  afterEdit,
  isGrp,
}: {
  isOpen: boolean;
  onCancel: () => void;
  currentIProductId: string;
  initialData: IFormData;
  setFormData: Function;
  afterEdit: Function;
  isGrp?: boolean;
}) {
  const t = useTrans('label.commission_setup,otr.common');
  const [commissionformData, setCommissionFormData] = useState(initialData);
  const [defaultTransactionData, setDefaultTransactionData] = useState({ id: '', name: '' });

  useEffect(() => {
    setDefaultTransactionData({ id: initialData.transaction_id || '', name: initialData.transaction_type || '' });
  }, []);

  const onFormChange = (name: string, value: any) => {
    setCommissionFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  };

  const handleUpdateCommission = () => {
    setFormData((prevFormData: IFormData[]) => {
      return prevFormData.map((product) => {
        if (product.id === currentIProductId) {
          // Check if commission_type is being changed
          if (commissionformData.commission_type && commissionformData.commission_type !== product.commission_type) {
            // Update all type fields in revised_commission_percent to match new commission_type
            const updatedRevisedCommission = product.revised_commission_percent?.map((item) => ({
              ...item,
              type: commissionformData.commission_type,
            }));

            return {
              ...product,
              ...commissionformData,
              revised_commission_percent: updatedRevisedCommission,
            };
          }
          return { ...product, ...commissionformData };
        }
        return product;
      });
    });
    toast.success(t('commission_updated_successfully'));
    afterEdit();
    onCancel();
  };

  return (
    <Modal isOpen={isOpen} onBackdrop={() => onCancel()}>
      <ModalHeader title={t('edit_insurer_product_commission')} onClose={() => onCancel()} />
      <ModalBody>
        <div className="row">
          <div className="col-12 mb-3">
            <div className="custom-select">
              <Label htmlFor="transaction_type" label={t('transaction_type')} />
              {!isGrp ? (
                <AsyncSelect
                  defaultValue={defaultTransactionData}
                  onChange={(_, data) => {
                    setDefaultTransactionData(data);
                    onFormChange('transaction_type', data?.name);
                    onFormChange('transaction_id', data?.id);
                  }}
                  className="form-control error-transaction_type"
                  loadOptions={fetchAllTransationTypeData}
                  option={{
                    value: 'id',
                    label: 'name',
                  }}
                />
              ) : (
                <Input value={defaultTransactionData.name} disabled />
              )}
            </div>
          </div>
          {/* Brokerage Commission Section */}
          <div className="col-12  my-3">
            <div className="row">
              <div className="col-12 col-md-6 mb-3">
                <Label htmlFor="brokerage_commission_type" label={t('commission_type')} />
                <div className="mb-3 d-flex flex-row gap-2 align-items-center">
                  <input
                    type="radio"
                    id="fixed"
                    name="percentage_method"
                    value="fixed"
                    className="mb-2"
                    onChange={(e) => onFormChange('brokerage_commission_type', e.target.value)}
                    checked={commissionformData?.brokerage_commission_type === 'fixed'}
                  />
                  <Label htmlFor="fixed" label={t('fixed')} />
                  <input
                    type="radio"
                    id="percentage"
                    name="percentage_method"
                    value="percentage"
                    className="mb-2"
                    onChange={(e) => onFormChange('brokerage_commission_type', e.target.value)}
                    checked={commissionformData?.brokerage_commission_type === 'percentage'}
                  />
                  <Label htmlFor="percentage" label={t('percentage')} />
                </div>
              </div>
              <div className="col-12 col-md-6 mb-3">
                <Input
                  label={t('brokerage_revenue')}
                  value={commissionformData?.brokerage_commission_value}
                  onChange={(e) => onFormChange('brokerage_commission_value', e.target.value)}
                  className="form-control error-brokerage_commission_value"
                  name="brokerage_commission_value"
                  type="number"
                  isRequired
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
                  <input
                    type="radio"
                    id="a_fixed"
                    name="a_percentage_method"
                    value="fixed"
                    className="mb-2"
                    onChange={(e) => onFormChange('commission_type', e.target.value)}
                    checked={commissionformData?.commission_type === 'fixed'}
                  />
                  <Label htmlFor="a_fixed" label={t('fixed')} />
                  <input
                    type="radio"
                    id="a_percentage"
                    name="a_percentage_method"
                    value="percentage"
                    className="mb-2"
                    onChange={(e) => onFormChange('commission_type', e.target.value)}
                    checked={commissionformData?.commission_type === 'percentage'}
                  />
                  <Label htmlFor="a_percentage" label={t('percentage')} />
                </div>
              </div>
              <div className="col-12 col-md-6">
                <Input
                  label={t('agent_commission')}
                  value={commissionformData?.commission_value}
                  onChange={(e) => onFormChange('commission_value', e.target.value)}
                  className="form-control error-commission_value"
                  name="commission_value"
                  type="number"
                  isRequired
                />
              </div>
            </div>
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('update')} type="button" width="sm" onClick={handleUpdateCommission} />
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default AddCommison;
