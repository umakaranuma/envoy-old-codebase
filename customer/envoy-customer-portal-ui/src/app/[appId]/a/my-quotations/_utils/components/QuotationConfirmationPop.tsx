import { useTrans } from '@/helpers/services/lang/langService';
import { PopConfirm } from '@apptimus-ui/ui-element';
import React from 'react';

function QuotationConfirmationPop({ trigger, quotationId, handleOnConfirm }: { trigger: any; quotationId: any; handleOnConfirm: Function }) {
  const t = useTrans('label.my_quotation,otr.common');
  return (
    <PopConfirm
      trigger={trigger}
      onConfirm={(callback, setLoader) => {
        handleOnConfirm(quotationId, callback, setLoader);
      }}
      onCancel={(callback) => callback()}
      placement="left"
      title={t('quotation_confirmation')}
      body={t('are_you_sure_you_want_to_confirm_this_quotation_once_confirmed_your_quotation_id_will_be_processed_and_the_policy_will_be_generated_this_action_cannot_be_undone')}
      confirmText={t('yes')}
      cancelText={t('cancel')}
    />
  );
}

export default QuotationConfirmationPop;
