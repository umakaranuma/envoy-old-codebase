import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Input } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { getOneNotes } from '../../../api-service';
import { INotes } from '../../../model';

function ViewNotes({ isOpen, viewId, onClose, entityId }: { isOpen: boolean; viewId: string; onClose: Function; entityId: string }) {
  const t = useTrans('label.sales_managements,otr.common');

  const [data, setData] = useState({} as INotes);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneNotes(entityId, viewId);
      responseData?.is_success && setData(responseData.result);
    };

    if (viewId) {
      fetchData();
    }
  }, [viewId]);

  const handleEditTaskConfig = () => {
    onClose();
    setTimeout(() => {}, 100);
  };

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('notes')} onClose={() => onClose()} />
      <ModalBody>
        <div className="row">
          <div className="col-12 col-md-12 mb-3">
            <Input type="text" label={t('content')} value={data?.notes} />
          </div>
          <div className="fs-5 fw-medium mb-2">State</div>
          <div className="d-flex gap-2">
            <input type="checkbox" checked={Boolean(data?.is_high_priority)} className=" form-check error-is_high_priority" name="is_high_priority" />
            <div>High Priority</div>
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('edit_task_details')} type="submit" width="sm" onClick={handleEditTaskConfig} />
          <Button text={t('close')} color="light" width="sm" onClick={() => onClose()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default ViewNotes;
