import { useEffect, useState } from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button } from '@apptimus-ui/ui-element';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import { getOneAttribute } from '../../api-service';
import { useParams } from 'next/navigation';
import { IAttribute } from '../../model';

export const ViewAttribute = ({ isOpen, viewId, onClose }: { isOpen: boolean; viewId: string; onClose: Function }) => {
  const t = useTrans('label.form,otr.common');

  const [data, setData] = useState({} as IAttribute);
  const [skeleton, setSkeleton] = useState(true);
  const params = useParams();
  const formId = params.id as string;

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneAttribute(formId, viewId);
      responseData?.is_success && (setData(responseData.result), setSkeleton(false));
    };

    if (viewId) {
      setSkeleton(true);
      fetchData();
    }
  }, [viewId]);

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('view_entity', { entity: t('attribute') })} onClose={() => onClose()} />
      <ModalBody>
        <div className="row">
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('title')} value={data?.title || '-'} skeleton={skeleton} />
          </div>
          {/* <div className="col-12 col-md-6 mb-3">
            <Description label={t('description')} value={data?.description || '-'} skeleton={skeleton} />
          </div> */}
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('close')} color="light" width="sm" onClick={() => onClose()} />
        </div>
      </ModalFooter>
    </Modal>
  );
};
