import { useTrans } from '@/helpers/services/lang/langService';
import { PopConfirm } from '@apptimus-ui/ui-element';
import React from 'react';

function ConfirmationPop({ trigger, entityId, handleOnSubmit, onClose }: { trigger: any; entityId: any; handleOnSubmit: Function; onClose?: Function }) {
  const t = useTrans('otr.common');

  return (
    <PopConfirm
      trigger={trigger}
      onConfirm={(callback, setLoader) => {
        handleOnSubmit(entityId, callback, setLoader, onClose);
      }}
      onCancel={(callback) => callback()}
      placement="left"
      title={t('confirm')}
      body={t('confirmation_msg')}
      confirmText={t('yes')}
      cancelText={t('cancel')}
    />
  );
}

export default ConfirmationPop;
