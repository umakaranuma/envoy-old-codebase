import { ImageDragAndDrop } from '@/components/others/page-related/ImageDragAndDrop';
import { form } from '@/constans/Form';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { AsyncSelect } from '@apptimus-ui/select';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';
import { fetchAllInvoices } from '../../../service';

function UploadReceipt({ isOpen, onCancel, setOpenSuccessMsg }: { isOpen: boolean; onCancel: Function; setOpenSuccessMsg: Function }) {
  const t = useTrans('label.my_policy,otr.common,be.msg');
  const [isFormProcessing, _setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({
    paid_amount: 0,
    endorsement_type_id: '',
    invoice_amount: 'LKR 0.00',
    outstanding_amount: 'LKR 0.00',
  });

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    handleOpenSuccessMsg();
    // clearError(form.settlement.store);
    //setIsFormProcessing(true);
    // try {
    //   const responseData = await CreateEndorsementRequests({ ...formData, issued_policy_id: policyId });
    //   setIsFormProcessing(false);

    //   if (responseData.status_code === 417) {
    //     printError(responseData.result, form.settlement.store, tBe);
    //   }

    //   if (responseData.is_success) {
    //     afterSave();
    //     setFormData(initEndorsementCreate);
    //     handleOpenEmail(responseData.result);
    //     toaster.success(tBe(responseData.message));
    //   }
    // } catch (error) {
    //   console.error('An error occurred:', error);
    // }
  }

  const handleOpenSuccessMsg = () => {
    onCancel();
    setTimeout(() => {
      setOpenSuccessMsg(formData.endorsement_type_id);
    }, 100);
  };

  return (
    <Modal isOpen={isOpen} size="lg" scrollable>
      <ModalHeader title={t('make_a_payment')} onClose={() => onCancel()} />
      <ModalBody>
        <div id={`${form.settlement.store}`}>
          <div className="row">
            <div className="fs-13 fw-semibold mb-3">{t('payment_information')}</div>
            <div className="col-12 col-md-6 mb-3 custom-select">
              <Label label={t('select_policy_number')} isRequired />
              <AsyncSelect
                onChange={() => {}}
                className="form-control error-endorsement_type_id"
                option={{ label: 'name', value: 'id' }}
                isSearchable={false}
                loadOptions={(searchValue: any, currentPage: any) => fetchAllInvoices(searchValue, currentPage, '2')}
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input label={t('debit_note_number')} isRequired value={formData.invoice_amount} className="form-control error-cover_value" name="cover_values" disabled />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                label={t('paid_amount')}
                isRequired
                value={formData.paid_amount}
                className="form-control error-cover_value"
                name="cover_values"
                onChange={(e) => onFormChange('paid_amount', e.target.value)}
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input label={t('outstanding_amount')} value={formData.outstanding_amount} className="form-control error-cover_value" name="cover_values" disabled />
            </div>
            <div className="col-12 mb-3">
              <Label label={t('upload_receipt')} isRequired />
              <ImageDragAndDrop htmlFor={'receipt'} />
            </div>
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          <Button text={t('submit')} type="submit" width="sm" isLoading={isFormProcessing} onClick={onSubmit} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default UploadReceipt;
