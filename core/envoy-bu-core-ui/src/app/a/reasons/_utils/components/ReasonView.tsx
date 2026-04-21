import { useTrans } from '@/helpers/services/lang/langService';
import React, { useEffect, useState } from 'react';
import { IReasonData } from '../model';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Description } from '@/components/others/Description';
import { Button, Skeleton } from '@apptimus-ui/ui-element';
import { getOneReason } from '../api-service';

export const ReasonView = ({ isOpen, viewId, onClose, setEditId }: { isOpen: boolean; viewId: string; onClose: Function; setEditId: Function }) => {
  const t = useTrans('label.reason,otr.common');
  const [data, setData] = useState({} as IReasonData);
  const [skeleton, setSkeleton] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneReason(viewId);
      responseData?.is_success && (setData(responseData.result), setSkeleton(false));
    };

    if (viewId) {
      setSkeleton(true);
      fetchData();
    }
  }, [viewId]);

  const handleEdit = () => {
    onClose();
    setTimeout(() => {
      setEditId(viewId);
    }, 100);
  };

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('reason')} onClose={() => onClose()} />
      <ModalBody>
        <div className="d-flex row">
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('reason_type')} value={data?.type || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('reason')} value={data?.reason || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('description')} value={data?.description || '-'} skeleton={skeleton} />
          </div>
        </div>
        <div className="mb-3">
          {skeleton ? (
            <Skeleton height="20px" width="140px" />
          ) : (
            <>
              <input type="checkbox" checked={data.allows_custom_reason} readOnly />
              <span className="ms-2 fs-14">{t('allow_custom_reason')}</span>
            </>
          )}
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('edit')} type="submit" width="sm" onClick={handleEdit} />
          <Button text={t('close')} color="light" width="sm" onClick={() => onClose()} />
        </div>
      </ModalFooter>
    </Modal>
  );
};
