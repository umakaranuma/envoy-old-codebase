import { useTrans } from '@/helpers/services/lang/langService';
import { PopConfirm } from '@apptimus-ui/ui-element';
import React from 'react';

function DeleteConfirmPop({ trigger, deleteId, handleOnDelete, onClose }: { trigger: any; deleteId: any; handleOnDelete: Function; onClose?: Function }) {
  const t = useTrans('otr.common');

  return (
    <PopConfirm
      trigger={trigger}
      onConfirm={(callback, setLoader) => {
        handleOnDelete(deleteId, callback, setLoader, onClose);
      }}
      onCancel={(callback) => callback()}
      placement="left"
      title={t('confirm')}
      body={t('delete_confirmation_msg')}
      confirmText={t('yes')}
      cancelText={t('cancel')}
    />
  );
}

export default DeleteConfirmPop;
