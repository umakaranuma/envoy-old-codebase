import { useTrans } from '@/helpers/services/lang/langService';
import { PopConfirm } from '@apptimus-ui/ui-element';
import React from 'react';

function ConfirmationPop({ trigger, entityId, handleOnSubmit, onClose, title = 'confirm' }: { trigger: any; entityId: any; handleOnSubmit: Function; onClose?: Function; title?: string }) {
  const t = useTrans('otr.common');

  return (
    <PopConfirm
      trigger={trigger}
      onConfirm={(callback, setLoader) => {
        handleOnSubmit(entityId, callback, setLoader, onClose);
      }}
      onCancel={(callback) => callback()}
      placement="right"
      title={t(`${title}`)}
      body={t('confirmation_msg')}
      confirmText={t('yes')}
      cancelText={t('cancel')}
    />
  );
}

export default ConfirmationPop;
