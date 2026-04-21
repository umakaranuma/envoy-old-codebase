import { form } from '@/constans/Form';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';

function EditMapping({ isOpen, onCancel }: { isOpen: boolean; onCancel: () => void }) {
  const t = useTrans('label.invoice,otr.common');
  const [formData, setFormData] = useState({
    field_name: '',
    field_type: '',
  });
  const [isFormProcessing, _setIsFormProcessing] = useState(false);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData: any) => ({ ...prevFormData, [name]: value }));
  };

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('edit_mapping_details')} onClose={() => onCancel()} />
      <form onSubmit={() => {}} id={`${form.field.store}`}>
        <ModalBody>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Input
                isRequired
                label={t('invoice_no')}
                value={formData.field_name}
                onChange={(e) => onFormChange('field_name', e.target.value)}
                className="form-control error-field_name"
                name="field_name"
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                isRequired
                label={t('invoice_date')}
                value={formData.field_name}
                onChange={(e) => onFormChange('invoice_date', e.target.value)}
                className="form-control error-field_name"
                name="invoice_date"
                type="date"
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                isRequired
                label={t('policy_info')}
                value={formData.field_name}
                onChange={(e) => onFormChange('policy_info', e.target.value)}
                className="form-control error-field_name"
                name="policy_info"
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                isRequired
                label={t('insurer_info')}
                value={formData.field_name}
                onChange={(e) => onFormChange('insurer_info', e.target.value)}
                className="form-control error-field_name"
                name="insurer_info"
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                isRequired
                label={t('settled_amount')}
                value={formData.field_name}
                onChange={(e) => onFormChange('settled_amount', e.target.value)}
                className="form-control error-field_name"
                name="settled_amount"
                type="number"
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                isRequired
                label={t('outstanding_amount')}
                value={formData.field_name}
                onChange={(e) => onFormChange('outstanding_amount', e.target.value)}
                className="form-control error-field_name"
                name="outstanding_amount"
                type="number"
              />
            </div>
            {/* <div className="col-12 col-md-6 custom-select">
                            <Label label={t('data_type')} isRequired />
                            <AsyncSelect
                                onChange={(value) => onFormChange('policy_id', value)}
                                className="form-control error-policy_id"
                                option={{ label: 'brokerage_policy_id', value: 'id' }}
                                isSearchable={true}
                                loadOptions={(searchValue: any, currentPage: any) => fetchAllIssuedPolicies(searchValue, currentPage)}
                            />
                        </div> */}
          </div>
        </ModalBody>
        <ModalFooter>
          <div className="d-flex justify-content-end gap-2">
            <Button text={t('update')} type="submit" width="sm" isLoading={isFormProcessing} />
            <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          </div>
        </ModalFooter>
      </form>
    </Modal>
  );
}

export default EditMapping;
