import { useTrans } from '@/helpers/services/lang/langService';
import React, { useEffect, useState } from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Description } from '@/components/others/Description';
import { Button } from '@apptimus-ui/ui-element';
import { IGeneralLedgerAccount } from '../../model';
import { getOnechartOfAccounts } from '../../api-service';

export const ChartOfAccountsView = ({ isOpen, viewId, onClose, setEditId }: { isOpen: boolean; viewId: string; onClose: Function; setEditId: Function }) => {
  const t = useTrans('label.general_ledger,otr.common');
  const [data, setData] = useState({} as IGeneralLedgerAccount);
  const [skeleton, setSkeleton] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      // Fetch the data for the given viewId (implement as needed)
      // Example:
      const response = await getOnechartOfAccounts(viewId);
      if (response?.is_success) {
        setData(response.result);
        setSkeleton(false);
      }
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
      <ModalHeader title={'Chart of Accounts Details'} onClose={() => onClose()} />
      <ModalBody>
        <div className="d-flex row">
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('account_name')} value={data?.account_name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('account_type')} value={data?.account_type || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 mb-3">
            <Description label={t('description')} value={data?.description || '-'} skeleton={skeleton} />
          </div>
        </div>
      </ModalBody>
      <ModalFooter>
        <div className="d-flex justify-content-end gap-2">
          <Button text={'Edit'} type="submit" width="sm" onClick={handleEdit} />
          <Button text={'Close'} color="light" width="sm" onClick={() => onClose()} />
        </div>
      </ModalFooter>
    </Modal>
  );
};
