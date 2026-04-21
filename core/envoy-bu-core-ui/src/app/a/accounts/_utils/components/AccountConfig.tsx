import { toaster } from '@/helpers/services/toaster';
import { Modal, ModalBody, ModalFooter, ModalHeader } from '@apptimus-ui/modal';
import { Button, Skeleton } from '@apptimus-ui/ui-element';
import { useEffect, useState } from 'react';
import { initCustConfigFormData } from '../model';
import { getCustomerConfig, saveCustomerConfig } from '../api-service';
import { useTrans } from '@/helpers/services/lang/langService';
import { clearError } from '@/helpers/handlers/validationErrorHandler';
import { Description } from '@/components/others/Description';
import { form } from '@/constans/Form';
import { Flexicon } from '@apptimus-ui/flexicon';

export const AccountConfig = ({
  isOpen,
  currentConfigId,
  afterConfig,
  onCancel,
  currentConfigData,
}: {
  isOpen: boolean;
  currentConfigId: string;
  onCancel: () => void;
  afterConfig: () => void;
  currentConfigData: any;
}) => {
  const t = useTrans('label.accounts,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initCustConfigFormData);
  const [isLoading, setIsLoading] = useState(true);
  const [accEmail, setAccEmail] = useState(null);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  useEffect(() => {
    onFormChange('name', currentConfigData.name);
    onFormChange('customer_id', currentConfigData.id);
    const fetchData = async () => {
      try {
        setIsLoading(true);
        const responseData = await getCustomerConfig(currentConfigId);
        if (responseData?.is_success) {
          if (responseData.result.email) {
            setAccEmail(responseData.result.email);
            onFormChange('email', responseData.result.email);
            setIsLoading(false);
          } else {
            onFormChange('email', null);
            setIsLoading(false);
          }
        }
      } catch (error) {
        console.error('Failed to fetch customer config:', error);
        toaster.error('Failed to load customer configuration');
      }
    };

    if (currentConfigId) {
      fetchData();
    }
  }, [currentConfigId, currentConfigData]);

  async function onSubmit() {
    clearError(form.customres_crud.store);
    setIsFormProcessing(true);
    try {
      const responseData = await saveCustomerConfig(formData);
      if (responseData.status_code === 417) {
        toaster.error(responseData.message);
        return;
      }
      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setFormData(initCustConfigFormData);
        afterConfig();
      }
    } catch (error) {
      console.error('An error occurred:', error);
      toaster.error('Failed to update customer configuration');
    } finally {
      setIsFormProcessing(false);
    }
  }

  return (
    <Modal isOpen={isOpen} onBackdrop={onCancel}>
      <ModalHeader title={t('configure_portal_access')} onClose={onCancel} />
      <ModalBody>
        {isLoading ? (
          <Skeleton width="100%" height="100px" />
        ) : (
          <>
            {accEmail === null || accEmail === '' ? (
              <div className="border border-2 border-light d-inline-block rounded-3">
                <div className="d-md-flex gap-3 p-3">
                  <div className="mb-3 mb-md-2">
                    <Flexicon icon="alert-square" variant="line" className="text-warning" />
                  </div>
                  <div>
                    <div className="mb-3 mb-md-2">
                      <div className="fw-medium">{t('you_have_not_entered_an_email_id_for_this_account_please_enter_an_email_id_and_try_again')}</div>
                      <div className="text-muted">{t('missing_email_address_for_this_account')}</div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="row" id={`${form.customres_crud.store}`}>
                <div className="col-12 col-md-6 mb-3">
                  <Description label={t('name')} value={currentConfigData?.name || '-'} />
                </div>
                <div className="col-12 col-md-6 mb-3">
                  <Description label={t('email')} value={accEmail || '-'} />
                </div>
              </div>
            )}
          </>
        )}
      </ModalBody>
      {!isLoading && (
        <ModalFooter>
          {accEmail === null || accEmail === '' ? (
            <div className="d-flex justify-content-end gap-2">
              <Button text={t('ok')} type="button" width="sm" onClick={onCancel} />
            </div>
          ) : (
            <div className="d-flex justify-content-end gap-2">
              <Button text={t('save')} type="submit" width="sm" isLoading={isFormProcessing} onClick={onSubmit} />
              <Button text={t('cancel')} color="light" width="sm" onClick={onCancel} />
            </div>
          )}
        </ModalFooter>
      )}
    </Modal>
  );
};
