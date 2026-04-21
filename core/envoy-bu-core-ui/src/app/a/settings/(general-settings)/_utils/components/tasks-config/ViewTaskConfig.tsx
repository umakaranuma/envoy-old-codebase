import { useEffect, useState } from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button } from '@apptimus-ui/ui-element';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import { ITaskConfigs } from '../../model';
import { getOneTaskConfigs } from '../../api-service';

export const ViewTaskConfig = ({ isOpen, viewId, onClose, setEdit }: { isOpen: boolean; viewId: string; onClose: Function; setEdit: Function }) => {
  const t = useTrans('label.general_settings,otr.common');

  const [data, setData] = useState({} as ITaskConfigs);
  const [skeleton, setSkeleton] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneTaskConfigs(viewId);
      responseData?.is_success && (setData(responseData.result), setSkeleton(false));
    };

    if (viewId) {
      setSkeleton(true);
      fetchData();
    }
  }, [viewId]);

  const handleEditTaskConfig = () => {
    onClose();
    setTimeout(() => {
      setEdit(viewId);
    }, 100);
  };

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('task_details')} onClose={() => onClose()} />
      <ModalBody>
        <div className="row">
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('task')} value={data?.task || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('task_type')} value={data?.task || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('expected_time_period_to_complete')} value={data?.expected_days || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('expected_time_to_send_reminder')} value={data?.reminder_expected_days || '-'} skeleton={skeleton} />
          </div>
          {/* <div className="col-12 col-md-6 mb-3">
            <Description label={t('assigned_stage')} value={data?.opportunity_status_id || '-'} skeleton={skeleton} />
          </div> */}
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
};
