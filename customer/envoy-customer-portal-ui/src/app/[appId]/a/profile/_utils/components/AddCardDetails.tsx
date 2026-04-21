import { form } from '@/constans/Form';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input, Label } from '@apptimus-ui/ui-element';
import React, { useState } from 'react';

function AddCardDetails({ isOpen, onCancel }: { isOpen: boolean; onCancel: Function }) {
  const t = useTrans('label.profile,otr.common,be.msg');
  const [isFormProcessing, _setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState({
    card: '',
    name_on_the_card: '',
    card_number: '',
    expiry_month_and_year: '',
    cvv: '',
  });

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    // clearError(form.card_details.store);
    //setIsFormProcessing(true);
    // try {
    //   const responseData = await CreateEndorsementRequests({ ...formData, issued_policy_id: policyId });
    //   setIsFormProcessing(false);
    //   if (responseData.status_code === 417) {
    //     printError(responseData.result, form.card_details.store, tBe);
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

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('add_card_details')} onClose={() => onCancel()} />
      <ModalBody>
        <div id={`${form.card_details.store}`}>
          <div className="row">
            <div className="mb-3 d-flex flex-row gap-2 align-items-center">
              <div className="d-flex flex-row align-items-center gap-2">
                <input type="radio" id="visa" name="card" value="visa" className="mb-2" onChange={(e) => onFormChange('card', e.target.value)} />
                <Label htmlFor="visa" label="Visa" />
                <div className="border border-light rounded-1 p-1 mb-2 px-2">
                  <svg width="33" height="12" viewBox="0 0 33 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path
                      fillRule="evenodd"
                      clipRule="evenodd"
                      d="M8.33406 11.1451H5.58774L3.52833 3.05728C3.43058 2.68524 3.22304 2.35634 2.91774 2.20132C2.15584 1.81176 1.31628 1.50172 0.400391 1.34536V1.03398H4.8245C5.43509 1.03398 5.89303 1.50172 5.96936 2.04495L7.03789 7.87898L9.78287 1.03398H12.4529L8.33406 11.1451ZM13.9794 11.1451H11.3857L13.5214 1.03398H16.1151L13.9794 11.1451ZM19.4707 3.83507C19.547 3.29049 20.0049 2.9791 20.5392 2.9791C21.3788 2.90092 22.2933 3.05729 23.0565 3.4455L23.5145 1.26853C22.7512 0.957146 21.9117 0.800781 21.1498 0.800781C18.6324 0.800781 16.8007 2.20132 16.8007 4.1451C16.8007 5.62383 18.0982 6.40026 19.0141 6.868C20.0049 7.3344 20.3865 7.64578 20.3102 8.11218C20.3102 8.81178 19.547 9.12316 18.7851 9.12316C17.8692 9.12316 16.9533 8.88996 16.1151 8.5004L15.6571 10.6787C16.573 11.0669 17.5639 11.2233 18.4798 11.2233C21.3024 11.3001 23.0565 9.90094 23.0565 7.8008C23.0565 5.15608 19.4707 5.00106 19.4707 3.83507ZM32.1337 11.1451L30.0743 1.03398H27.8623C27.4043 1.03398 26.9464 1.34536 26.7937 1.81176L22.9802 11.1451H25.6502L26.1831 9.66774H29.4637L29.769 11.1451H32.1337ZM28.2439 3.75689L29.0058 7.56761H26.8701L28.2439 3.75689Z"
                      fill="#172B85"
                    />
                  </svg>
                </div>
              </div>
              <div className="d-flex flex-row align-items-center gap-2">
                <input type="radio" id="master" name="card" value="master" className="mb-2" onChange={(e) => onFormChange('card', e.target.value)} />
                <Label htmlFor="master" label="Master" />
                <div className="border border-light rounded-1 p-1 mb-2 px-2">
                  <svg width="30" height="19" viewBox="0 0 30 19" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path
                      fillRule="evenodd"
                      clipRule="evenodd"
                      d="M14.9053 16.4396C13.3266 17.7704 11.2787 18.5737 9.04092 18.5737C4.04776 18.5737 0 14.5741 0 9.64036C0 4.70662 4.04776 0.707031 9.04092 0.707031C11.2787 0.707031 13.3266 1.51036 14.9053 2.84109C16.484 1.51036 18.5319 0.707031 20.7697 0.707031C25.7628 0.707031 29.8106 4.70662 29.8106 9.64036C29.8106 14.5741 25.7628 18.5737 20.7697 18.5737C18.5319 18.5737 16.484 17.7704 14.9053 16.4396Z"
                      fill="#ED0006"
                    />
                    <path
                      fillRule="evenodd"
                      clipRule="evenodd"
                      d="M14.9053 16.4396C16.8492 14.8011 18.0818 12.363 18.0818 9.64036C18.0818 6.91776 16.8492 4.47962 14.9053 2.84108C16.484 1.51036 18.5319 0.707031 20.7697 0.707031C25.7628 0.707031 29.8106 4.70662 29.8106 9.64036C29.8106 14.5741 25.7628 18.5737 20.7697 18.5737C18.5319 18.5737 16.484 17.7704 14.9053 16.4396Z"
                      fill="#F9A000"
                    />
                    <path
                      fillRule="evenodd"
                      clipRule="evenodd"
                      d="M14.905 16.4403C16.8489 14.8018 18.0815 12.3636 18.0815 9.64105C18.0815 6.91846 16.8489 4.48033 14.905 2.8418C12.9611 4.48033 11.7285 6.91846 11.7285 9.64105C11.7285 12.3636 12.9611 14.8018 14.905 16.4403Z"
                      fill="#FF5E00"
                    />
                  </svg>
                </div>
              </div>
            </div>
            <div className="col-12 mb-3">
              <Input
                label={t('name_on_the_card')}
                isRequired
                value={formData.name_on_the_card}
                className="form-control error-name_on_the_card"
                name="name_on_the_card"
                onChange={(e) => onFormChange('name_on_the_card', e.target.value)}
              />
            </div>
            <div className="col-12 mb-3">
              <Input
                label={t('card_number')}
                isRequired
                value={formData.card_number}
                className="form-control error-card_number"
                name="card_number"
                onChange={(e) => onFormChange('card_number', e.target.value)}
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input
                label={t('expiry_month_and_year')}
                value={formData.expiry_month_and_year}
                className="form-control error-expiry_month_and_year"
                name="expiry_month_and_year"
                onChange={(e) => onFormChange('expiry_month_and_year', e.target.value)}
                placeholder="MM/YY"
                isRequired
              />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input label={t('cvv')} value={formData.cvv} className="form-control error-cvv" name="cvv" onChange={(e) => onFormChange('cvv', e.target.value)} placeholder="CVV" isRequired />
            </div>
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
          <Button text={t(`submit`)} type="submit" width="sm" isLoading={isFormProcessing} onClick={onSubmit} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default AddCardDetails;
