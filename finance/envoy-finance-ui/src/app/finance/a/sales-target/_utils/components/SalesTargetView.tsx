import { useEffect, useState } from 'react';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button } from '@apptimus-ui/ui-element';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import { getOneSalesTarget } from '../api-service';
import { ISalesTargetResult } from '../model';
import { getCurrency } from '@/helpers/services/currencyService';
import { thousandSeparator } from '@/helpers/services/commonService';

export const SalesTargetView = ({ isOpen, viewId, onClose, activetab, setEditId }: { isOpen: boolean; viewId: string; onClose: Function; setEditId: Function; activetab: string }) => {
  const t = useTrans('label.sales_target,otr.common');
  const currency = getCurrency();
  const [data, setData] = useState({} as ISalesTargetResult);
  const [skeleton, setSkeleton] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const responseData = await getOneSalesTarget(viewId, activetab);
        if (responseData?.is_success) {
          setData(responseData.result);
          setSkeleton(false);
        }
      } catch (error) {
        console.error(error);
      }
    };

    if (viewId) {
      fetchData();
    }
  }, [viewId]);

  const handleEdit = () => {
    onClose();
    setEditId(viewId);
  };

  function getMonthName(monthNumber: number) {
    const monthKeys = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'];

    if (monthNumber >= 1 && monthNumber <= 12) {
      return t(monthKeys[monthNumber - 1]);
    }

    return '';
  }

  return (
    <Modal isOpen={isOpen} onBackdrop={() => onClose()}>
      <ModalHeader title={t('sales_target')} onClose={() => onClose()} />
      <ModalBody>
        <div className="row">
          <div className="col-12 col-md-6 mb-3">
            <Description
              label={activetab === 'individual' ? t('agent_info') : t('team_name')}
              value={activetab === 'individual' ? data?.agent_name || '-' : data?.team_name || '-'}
              skeleton={skeleton}
            />
          </div>
          {data.period_type === 'monthly' ? (
            <div className="col-12 col-md-6 mb-3">
              <Description label={t('target_period')} value={`${getMonthName(data.month)} ${data.year}`} skeleton={skeleton} />
            </div>
          ) : (
            <div className="col-12 col-md-6 mb-3">
              <Description label={t('target_period')} value={data?.year || '-'} skeleton={skeleton} />
            </div>
          )}
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('achieved')} value={data?.achieved !== null ? `${currency.code} ${thousandSeparator(data.achieved)}` : '0.00'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('target_amount')} value={data?.target_amount !== null ? `${currency.code} ${thousandSeparator(data.target_amount)}` : '-'} skeleton={skeleton} />
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
