'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import { Button } from '@apptimus-ui/ui-element';
import React from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';

function EmailSentSuccessfully({ isOpen, onCancel }: { isOpen: boolean; onCancel: Function }) {
  const t = useTrans('label.claim,otr.common');

  return (
    <Modal isOpen={isOpen} position="center">
      <ModalHeader title="" onClose={() => onCancel()} />
      <ModalBody>
        <div className="fw-semibold fs-15">{t('email_sent_successfully')}</div>
        <span className="text-muted fs-12">{t('email_comformation')}</span>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('continue')} width="sm" />
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default EmailSentSuccessfully;
