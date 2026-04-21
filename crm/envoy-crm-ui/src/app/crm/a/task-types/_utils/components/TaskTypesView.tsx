import { useTrans } from '@/helpers/services/lang/langService';
import React, { useEffect, useState } from 'react';
import { ITaskTypes } from '../model';
import { getOneTaskTypes } from '../api-service';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Description } from '@/components/others/Description';
import { Button } from '@apptimus-ui/ui-element';

export const TaskTypesView = ({ isOpen, viewId, onClose, setEditId }: { isOpen: boolean; viewId: string; onClose: Function; setEditId: Function }) => {
  const t = useTrans('label.task_types,otr.common');

  const [data, setData] = useState({} as ITaskTypes);
  const [skeleton, setSkeleton] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneTaskTypes(viewId);
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
      <ModalHeader title={t('task_types')} onClose={() => onClose()} />
      <ModalBody>
        <div className="row">
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('name')} value={data?.name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('description')} value={data?.description || '-'} skeleton={skeleton} />
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('edit')} type="submit" size="sm" width="sm" onClick={handleEdit} />
          <Button text={t('close')} color="light" size="sm" width="sm" onClick={() => onClose()} />
        </div>
      </ModalFooter>
    </Modal>
  );
};
