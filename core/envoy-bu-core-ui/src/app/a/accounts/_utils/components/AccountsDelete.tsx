import { useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { ConfirmationPopup } from '@/components/others/ConfirmationPopup';
import { deleteCustomers } from '../api-service';
import { useTrans } from '@/helpers/services/lang/langService';

export const AccountsDelete = ({ isOpen, deleteId, afterDelete, onCancel }: { isOpen: boolean; deleteId: string; afterDelete: Function; onCancel: Function }) => {
  if (!isOpen) {
    return null;
  }

  const t = useTrans('otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);

  const handleOnDelete = async () => {
    setIsFormProcessing(true);
    const responseData = await deleteCustomers(deleteId);
    setIsFormProcessing(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      afterDelete();
    }
  };

  return (
    <ConfirmationPopup
      msg={t('delete_confirmation_msg')}
      yesButtonLabel={t('delete')}
      noButtonLabel={t('cancel')}
      isOpen={isOpen}
      onYes={handleOnDelete}
      onCancel={() => onCancel()}
      isFormProcessing={isFormProcessing}
    />
  );
};
