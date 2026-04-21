import { useTrans } from '@/helpers/services/lang/langService';
import { PopConfirm } from '@apptimus-ui/ui-element';
import React from 'react';

function DraftConfirmPopup({ trigger, handleOnDraft, onClose, placement = 'right' }: { trigger: any; handleOnDraft: Function; onClose?: Function; placement?: 'top' | 'bottom' | 'left' | 'right' }) {
  const t = useTrans('otr.common');

  return (
    <PopConfirm
      trigger={trigger}
      onConfirm={(callback, setLoader) => {
        handleOnDraft(callback, setLoader, onClose);
      }}
      onCancel={(callback) => (callback(), onClose?.())}
      placement={placement}
      title={t('save_before_leaving')}
      body={t('leaving_now_will_discard_your_progress_save_it_as_a_draft_to_pick_up_where_you_left_off')}
      confirmText={t('yes')}
      cancelText={t('no')}
    />
  );
}

export default DraftConfirmPopup;
