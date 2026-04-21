import { useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { deleteEntityFlag } from '../../api-service';
import { Modal } from '@apptimus-ui/modal';
import { Flexicon } from '@apptimus-ui/flexicon';
import { IFlagResons } from '../../model';
import FlagDeleteConfirmPop from './FlagDeleteConfirmPop';

export const FlagDelete = ({ isOpen, entityId, afterDelete, onCancel, data }: { isOpen: boolean; entityId: string; afterDelete: Function; onCancel: Function; data: IFlagResons }) => {
  if (!isOpen) {
    return null;
  }

  const t = useTrans('label.sales_managements,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [_isFormProcessing, setIsFormProcessing] = useState(false);

  const handleOnDelete = async () => {
    setIsFormProcessing(true);
    const responseData = await deleteEntityFlag(entityId, data.id);
    setIsFormProcessing(false);

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      afterDelete();
    }
  };

  return (
    <Modal isOpen={isOpen} position="center">
      <div className="d-flex align-items-center justify-content-between gap-3 p-3">
        <div className="d-flex align-items-start gap-2">
          <div className="d-flex justify-content-center align-items-center gap-2" style={{ color: data.color }}>
            <div className="flag-bar" style={{ backgroundColor: data.color }}></div>
            <Flexicon icon="flag-01" variant="solid" size={30} />
          </div>
          <div className="">
            <p className="p-0 m-0">{data.name}</p>
            <span className="text-muted">{data.description}</span>
          </div>
        </div>
        <div className="d-flex align-items-center justify-content-center gap-2">
          <FlagDeleteConfirmPop
            trigger={
              <div className="d-flex align-items-center justify-content-center gap-1 flag-button pointer" style={{ backgroundColor: data.color }}>
                <span className="d-none d-sm-inline">{t('remove')}</span>
              </div>
            }
            deleteId={data.id}
            handleOnDelete={handleOnDelete}
          />
          {/* <DeleteConfirmPop trigger={ <div className="d-flex align-items-center justify-content-center gap-1 flag-button pointer" style={{ backgroundColor: data.color }}>
                <span className="d-none d-sm-inline">{t('remove')}</span>
              </div>} deleteId={data.id} {...{ handleOnDelete }} /> */}
          <div className="d-flex align-items-center justify-content-center pointer" style={{ color: data.color }} onClick={() => onCancel()}>
            <Flexicon icon="x-close" variant="line" />
          </div>
        </div>
      </div>
    </Modal>
  );
};
