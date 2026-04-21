import { useEffect, useState } from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button } from '@apptimus-ui/ui-element';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams } from 'next/navigation';
import { IForm } from '../../model';
import { getOneForm } from '../../api-service';

export const ViewForm = ({ isOpen, viewId, onClose }: { isOpen: boolean; viewId: string; onClose: Function }) => {
  const t = useTrans('label.product_categories,otr.common');

  const [data, setData] = useState({} as IForm);
  const [skeleton, setSkeleton] = useState(true);
  const params = useParams();
  const formId = params.categoryId as string;

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneForm(formId, viewId);
      responseData?.is_success && (setData(responseData.result), setSkeleton(false));
    };

    if (viewId) {
      setSkeleton(true);
      fetchData();
    }
  }, [viewId]);

  return (
    <Modal isOpen={isOpen}>
      <ModalHeader title={t('view_entity', { entity: t('form') })} onClose={() => onClose()} />
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
