import { Modal, ModalBody, ModalHeader } from '@apptimus-ui/modal';
import React, { useEffect, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { Skeleton } from '@apptimus-ui/ui-element';
import { IFormTemplate } from '@/components/others/common/form/template-modal';
import { IElements } from '../../../model';
import FormCreate from '@/components/others/common/form/FormCreate';
import { getOneRisk, updateOneRisk } from '@/app/policy/a/risk-register/_utils/api-service';

function EditRiskInfo({ isOpen, onCancel, afterSave, riskInfoId }: { isOpen: boolean; onCancel: Function; afterSave: Function; riskInfoId: string }) {
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [templateData, setTemplateData] = useState<IFormTemplate>({} as IFormTemplate);
  const t = useTrans('label.sales_managements,otr.common,be.msg');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await getOneRisk(riskInfoId);
        if (response?.is_success) {
          setTemplateData(response.result);
        }
        setLoading(false);
      } catch (error) {
        console.error('Error fetching form attributes:', error);
      }
    };

    if (riskInfoId) {
      fetchData();
    }
  }, [riskInfoId]);

  async function onSubmit(data: IElements[]) {
    setIsFormProcessing(true);
    try {
      const responseData = await updateOneRisk(riskInfoId, {
        // customer_id: customerId,
        // lead_id: opportunityId,
        // risk_type_id: typeId,
        values: data,
      });
      setIsFormProcessing(false);

      if (responseData.is_success) {
        afterSave();
        toaster.success(t(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
      setIsFormProcessing(false);
    }
  }

  return (
    <Modal isOpen={isOpen} size="xl" onBackdrop={() => onCancel()} scrollable={true}>
      <ModalHeader title={t('edit_risk_info')} onClose={() => onCancel()} />
      <ModalBody>
        {loading ? (
          <Skeleton width="100%" height="400px" />
        ) : (
          <FormCreate onBack={onCancel} isFormProcessing={isFormProcessing} onSubmit={(data: IElements[]) => onSubmit(data)} templateData={templateData} />
        )}
      </ModalBody>
    </Modal>
  );
}

export default EditRiskInfo;
