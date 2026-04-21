import { Modal, ModalBody, ModalHeader } from '@apptimus-ui/modal';
import React, { useEffect, useState } from 'react';
import { toaster } from '@/helpers/services/toaster';
import { useTrans } from '@/helpers/services/lang/langService';
import Link from 'next/link';
import { IElement, IFormTemplate } from '@/components/others/common/form/template-modal';
import { getFormsElements } from '@/components/others/common/form/api-service';
import FormCreate from '@/components/others/common/form/FormCreate';
import { CreateRisk } from '@/app/policy/a/risk-register/_utils/api-service';
import { Skeleton } from '@apptimus-ui/ui-element';
import { getAllOpportunityTypeFormAttributes } from '@/components/others/common/lead/api-service';

function AddInfo({
  isOpen,
  onCancel,
  afterSave,
  typeId,
  opportunityId,
  customerId,
}: {
  isOpen: boolean;
  onCancel: Function;
  afterSave: Function;
  typeId: string;
  opportunityId: string;
  customerId: string;
}) {
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [templateData, setTemplateData] = useState<IFormTemplate>({} as IFormTemplate);
  const t = useTrans('label.sales_managements,otr.common,be.msg');
  const [formId, setFormId] = useState('');
  const [loading, setLoading] = useState(true);
  const backURL = encodeURIComponent(window.location.pathname + window.location.search);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const responseData = await getAllOpportunityTypeFormAttributes(typeId, 'ONBOARDING');
        if (responseData?.is_success) {
          setFormId(responseData.result?.form_id?.toString() || '');
          const response = await getFormsElements(responseData.result?.form_id?.toString());
          if (response?.is_success) {
            setTemplateData(response.result);
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

  async function onSubmit(data: IElement[]) {
    setIsFormProcessing(true);
    try {
      const responseData = await CreateRisk({
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
            {formId === '' ? (
              <div className="text-center p-5 card">
                <div className="text-muted fs-15 fw-semibold my-2">{t('no_form_config')}</div>
                <Link className="text-primary clickable-text fs-14" href={`/a/product-categories/${typeId}?t=forms&backUrl=${backURL}`}>
                  {t('configure_it_now')}
                </Link>
              </div>
            ) : (
              <FormCreate onBack={onCancel} isFormProcessing={isFormProcessing} onSubmit={(data: IElement[]) => onSubmit(data)} templateData={templateData} />
            )}
          </>
        )}
      </ModalBody>
    </Modal>
  );
}

export default AddInfo;
