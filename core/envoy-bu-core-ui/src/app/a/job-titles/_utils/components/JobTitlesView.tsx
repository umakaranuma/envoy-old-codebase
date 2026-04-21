import { useEffect, useState } from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button } from '@apptimus-ui/ui-element';
import { getOneJobTitle } from '../api-service';
import { IJobtitle } from '../model';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';

export const JobTitlesView = ({ isOpen, viewId, onClose, setEditId }: { isOpen: boolean; viewId: string; onClose: Function; setEditId: Function }) => {
  const t = useTrans('label.job_titles,otr.common');
  const [data, setData] = useState({} as IJobtitle);
  const [skeleton, setSkeleton] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneJobTitle(viewId);
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
    <Modal isOpen={isOpen} onBackdrop={() => onClose()}>
      <ModalHeader title={t('job_title')} onClose={() => onClose()} />
      <ModalBody>
        <div className="row">
          <div className="col-12 mb-3">
            <Description label={t('title')} value={data?.title || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 mb-3">
            <Description label={t('description')} value={data?.description || '-'} skeleton={skeleton} />
          </div>
          {/* <div className="col-12 mb-3">
            <Description label={t('number_of_staffs_with_title')} value={data?.description || '-'} skeleton={skeleton} />
          </div> */}
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
