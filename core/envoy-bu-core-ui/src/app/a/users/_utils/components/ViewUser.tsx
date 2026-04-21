import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { getOneUser } from '../api-service';
import { IUser } from '../model';

function ViewUser({ isOpen, onCancel, viewId, setEditId }: { viewId: string; isOpen: boolean; onCancel: Function; setEditId: Function }) {
  const t = useTrans('label.user,otr.common');
  const [data, setData] = useState({} as IUser);
  const [skeleton, setSkeleton] = useState(true);
  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneUser(viewId);
      responseData?.is_success && (setData(responseData.result), setSkeleton(false));
    };

    if (viewId) {
      setSkeleton(true);
      fetchData();
    }
  }, [viewId]);

  const handleEdit = () => {
    onCancel();
    setTimeout(() => {
      setEditId(viewId);
    }, 100);
  };
  return (
    <Modal isOpen={isOpen} size="lg">
      <ModalHeader title={t('user_staff')} onClose={() => onCancel()} />
      <ModalBody>
        <div className="row">
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('salutation')} value={data?.salutation || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('first_name')} value={data?.first_name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('last_name')} value={data?.last_name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('staff_code')} value={data?.staff_code || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('sales_team')} value={data?.sales_team || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('user_role')} value={data?.role_name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('email')} value={data?.email || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('contact_number')} value={data?.contact_no || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('line_manager')} value={data?.line_manager || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('status')} value={data?.status || '-'} skeleton={skeleton} />
          </div>
        </div>
        <div className="row">
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('created_by')} value={data?.created_by || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('created_date')} value={data?.created_date || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('updated_by')} value={data?.updated_by || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('updated_date')} value={data?.updated_date || '-'} skeleton={skeleton} />
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={t('edit')} color="primary" width="sm" onClick={handleEdit} />
          <Button text={t('cancel')} color="light" width="sm" onClick={() => onCancel()} />
        </div>
      </ModalFooter>
    </Modal>
  );
}

export default ViewUser;
