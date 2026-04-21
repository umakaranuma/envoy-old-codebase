import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button } from '@apptimus-ui/ui-element';
import React from 'react';

function SuccessMessage({ isOpen, onCancel, invoiceNumber }: { isOpen: boolean; onCancel: Function; invoiceNumber: string }) {
  const t = useTrans('label.my_policy,otr.common,be.msg');
  return (
    <Modal isOpen={isOpen} scrollable>
      <ModalHeader title={`${t('receipt_submitted_successfully')} 🎉`} onClose={() => onCancel()} />
      <ModalBody>
        <div>
          <div className="text-muted fs-14 pb-3">{t('your_payment_receipt_has_been_received_and_is_under_review')}</div>
          <div className="pb-2">
            {t('thank_you_for_submitting_your_bank_transfer_receipt_for_policy')}
            <span className="fw-semibold"> {invoiceNumber}</span>
          </div>
          <div>{t('our_team_will_verify_your_payment_within_1_3_business_days_you_will_receive_an_email_notification_once_your_payment_is_confirmed_and_applied_to_your_policy')}</div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('ok')} type="submit" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default SuccessMessage;
