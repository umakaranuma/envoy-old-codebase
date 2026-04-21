import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { INotes } from '../../../model';
import { getOneNotes } from '@/components/others/common/lead/api-service';
import { Description } from '@/components/others/Description';

function NotesView({ isOpen, viewId, onClose, entityId }: { isOpen: boolean; viewId: string; onClose: Function; entityId: string }) {
  const t = useTrans('label.issued_policies,otr.common');

  const [data, setData] = useState({} as INotes);
  const [skeleton, setSkeleton] = useState(true);
  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneNotes(entityId, viewId);
      responseData?.is_success && setData(responseData.result);
      setSkeleton(false);
    };

    if (viewId) {
      fetchData();
    }
  }, [viewId]);

  // const handleEditTaskConfig = () => {
  //   onClose();
  //   setTimeout(() => {}, 100);
  // };

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('notes')} onClose={() => onClose()} />
      <ModalBody>
        <div className="row">
          <div className="col-12 col-md-12 mb-3">
            <Description label={t('content')} isTruncate={false} value={data?.notes || ''} skeleton={skeleton} />
          </div>
          <div className="d-flex gap-2">
            <input type="checkbox" disabled checked={Boolean(data?.is_high_priority)} className=" form-check error-is_high_priority" name="is_high_priority" />
            <div>High Priority</div>
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          {/* <Button text={t('edit_task_details')} type="submit" width="sm" onClick={handleEditTaskConfig} /> */}
          <Button text={t('close')} color="light" width="sm" onClick={() => onClose()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default NotesView;
