import { useEffect, useState } from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Badge, Button, Label } from '@apptimus-ui/ui-element';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import { getOnePartnerContact } from '../../api-service';
import { useParams } from 'next/navigation';
import { IContactDetail } from '../../model';

export const ViewContact = ({ isOpen, viewId, onClose, setEditId }: { isOpen: boolean; viewId: string; onClose: Function; setEditId: Function }) => {
  const t = useTrans('label.partners,otr.common');
  const params = useParams();
  const partnerId = params.partnerId?.toString() || '';
  const [data, setData] = useState({} as IContactDetail);
  const [skeleton, setSkeleton] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOnePartnerContact(partnerId, viewId);
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
    <Modal
      isOpen={isOpen}
      onBackdrop={() => {
        onClose();
      }}
      size={'lg'}
    >
      <ModalHeader title={t('view_entity', { entity: t('contact') })} onClose={() => onClose()} />
      <ModalBody>
        <div className="row">
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('salutation')} value={data?.title || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('contact_person_name')} value={data?.name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('email')} value={data?.email || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('contact_number')} value={data?.primary_contact || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <div className="w-100">
              <Label label={t('is_primary')} />
            </div>
            <Badge text={data.is_primary ? t('yes') : t('no')} color={data.is_primary ? 'success' : 'warning'} radius="pill" />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('remarks')} value={data?.remarks || '-'} skeleton={skeleton} />
          </div>
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
