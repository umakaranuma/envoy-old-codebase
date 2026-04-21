import { useEffect, useState } from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button } from '@apptimus-ui/ui-element';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import { getOneInteraction } from '../../api-service';
import { IInteractions } from '../../model';

export const InteractionsView = ({ isOpen, viewId, onClose, contactId }: { isOpen: boolean; viewId: string; onClose: Function; contactId: string }) => {
  const t = useTrans('label.contacts,otr.common');
  const [data, setData] = useState({} as IInteractions);
  const [skeleton, setSkeleton] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneInteraction(contactId, viewId);
      responseData?.is_success && (setData(responseData.result), setSkeleton(false));
    };

    if (viewId) {
      setSkeleton(true);
      fetchData();
    }
  }, [viewId]);

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('manage_interactions_details')} onClose={() => onClose()} />
      <ModalBody>
        <div className="row">
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('date')} value={data?.date || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('channel')} value={data?.channel || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('imitated_by')} value={data?.imitated_by || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('task')} value={data?.task || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('notes')} value={data?.notes || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('contact_by')} value={data?.contact_by || '-'} skeleton={skeleton} />
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('close')} color="light" size="sm" width="sm" onClick={() => onClose()} />
        </div>
      </ModalFooter>
    </Modal>
  );
};
