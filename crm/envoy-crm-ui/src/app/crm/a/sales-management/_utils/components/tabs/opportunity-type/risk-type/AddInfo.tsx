import { Modal, ModalBody, ModalHeader } from '@apptimus-ui/modal';
import React, { useEffect, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import { Skeleton } from '@apptimus-ui/ui-element';
import FormCreate from '@/components/others/common/forms/FormCreate';
import { IElements } from '../../../../model';
import { IFormTemplate } from '@/components/others/common/forms/models';
import { CreateRiskInfo, getAllFormsDetails, getAllOpportunityTypeConfig } from '../../../../api-service';

function AddInfo({
  isOpen,
  onCancel,
  afterSave,
  typeId,
  opportunityId,
  customerId,
  handleOpenConfig,
}: {
  isOpen: boolean;
  onCancel: Function;
  afterSave: Function;
  typeId: string;
  opportunityId: string;
  customerId: string;
  handleOpenConfig: Function;
}) {
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [templateData, setTemplateData] = useState<IFormTemplate>({} as IFormTemplate);
  const t = useTrans('label.sales_managements,otr.common,be.msg');
  const [isConfigured, setIsConfigured] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const responseData = await getAllOpportunityTypeConfig(typeId, 'ONBOARDING');
        if (responseData?.is_success) {
          if (responseData.result?.form_id) {
            setIsConfigured(true);
            const response = await getAllFormsDetails(responseData.result.form_id.toString());
            if (response?.is_success) {
              setTemplateData(response.result);
            }
          }
          setLoading(false);
        }
      } catch (error) {
        console.error('Error fetching form attributes:', error);
      }
    };

    if (typeId) {
      fetchData();
    }
  }, [typeId]);

  async function onSubmit(data: IElements[]) {
    setIsFormProcessing(true);
    try {
      const responseData = await CreateRiskInfo({
        customer_id: customerId,
        lead_id: opportunityId,
        risk_type_id: typeId,
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
      <ModalHeader title={t('add_new_entity', { entity: t('info') })} onClose={() => onCancel()} />
      <ModalBody>
        {loading ? (
          <Skeleton width="100%" height="400px" />
        ) : (
          <>
            {!isConfigured ? (
              <div className="panel text-center">
                <div className="text-muted fs-15 fw-semibold my-2">{t('no_form_config')}</div>
                <div className="text-primary clickable-text fs-14" onClick={() => handleOpenConfig()}>
                  {t('configure_it_now')}
                </div>
              </div>
            ) : (
              <FormCreate onBack={onCancel} isFormProcessing={isFormProcessing} onSubmit={(data: IElements[]) => onSubmit(data)} templateData={templateData} />
            )}
          </>
        )}
      </ModalBody>
    </Modal>
  );
}

export default AddInfo;
