import { useTrans } from '@/helpers/services/lang/langService';
import { PopConfirm } from '@apptimus-ui/ui-element';
import React from 'react';

function FlagDeleteConfirmPop({ trigger, deleteId, handleOnDelete, onClose }: { trigger: any; deleteId: any; handleOnDelete: Function; onClose?: Function }) {
  const t = useTrans('otr.common');

  return (
    <PopConfirm
      trigger={trigger}
      onConfirm={(callback, setLoading) => {
        setLoading(true);
        handleOnDelete(deleteId, callback, onClose);
        setTimeout(() => {
          setLoading(false);
          callback();
        }, 2000);
      }}
      onCancel={(callback) => callback()}
      placement="bottom"
      title={t('confirm')}
      body={t('delete_confirmation_msg')}
      confirmText={t('yes')}
      cancelText={t('cancel')}
    />
  );
}

export default FlagDeleteConfirmPop;
