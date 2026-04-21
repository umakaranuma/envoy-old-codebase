import { useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { ConfirmationPopup } from '@/components/others/ConfirmationPopup';
import { useTrans } from '@/helpers/services/lang/langService';
import { deleteType } from '../api-service';

export const ProductCategoriesDelete = ({ isOpen, deleteId, afterDelete, onCancel }: { isOpen: boolean; deleteId: string; afterDelete: Function; onCancel: Function }) => {
  const t = useTrans('otr.common,be.msg');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);

  const handleOnDelete = async () => {
    setIsFormProcessing(true);
    const responseData = await deleteType(deleteId);
    console.log(responseData, 'fefef');

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
