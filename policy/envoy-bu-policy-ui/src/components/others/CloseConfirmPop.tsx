import { useTrans } from '@/helpers/services/lang/langService';
import { PopConfirm } from '@apptimus-ui/ui-element';
import React from 'react';

function CloseConfirmPop({ trigger, handleOnClose, onClose }: { trigger: any; handleOnClose: Function; onClose?: Function }) {
  const t = useTrans('otr.common');

  return (
    <PopConfirm
      trigger={trigger}
      onConfirm={(callback, setLoader) => {
        handleOnClose(callback, setLoader, onClose);
      }}
      onCancel={(callback) => callback()}
      placement="left"
      title={t('want_to_exit')}
      body={t('close_confirmation_msg')}
      confirmText={t('yes')}
      cancelText={t('cancel')}
    />
  );
}

export default CloseConfirmPop;
