import ToggleButton from '@/components/others/page-related/ToggleButton';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { getNotificationSettingInfo, updateNotificationInfo } from '../api-service';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { form } from '@/constans/Form';
import { toaster } from '@/helpers/services/toaster';

export function NotificationSettings() {
  const t = useTrans('label.profile,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');

  const [formData, setFormData] = useState({
    policy_lifecycle_notifications: { push: false, email: false },
    payments_reminders: { push: false, email: false },
    account_security: { push: false, email: false },
    promotions_updates_optional: { push: false, email: false },
  });
  const [isFormProcessing, setIsFormProcessing] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getNotificationSettingInfo();
      if (responseData?.is_success) {
        const result = responseData.result;
        const mapValue = (val: string) => ({
          push: val === 'push' || val === 'both',
          email: val === 'email' || val === 'both',
        });
        setFormData({
          policy_lifecycle_notifications: mapValue(result.policy_lifecycle_notifications),
          payments_reminders: mapValue(result.payments_and_reminders),
          account_security: mapValue(result.account_and_security),
          promotions_updates_optional: mapValue(result.promotions_and_updates),
        });
      }
    };
    fetchData();
  }, []);

  const mapToApiValue = (obj: { push: boolean; email: boolean }) => {
    if (obj.push && obj.email) return 'both';
    if (obj.push) return 'push';
    if (obj.email) return 'email';
    return 'none';
  };

  async function onSubmit() {
    clearError(form.profile.update);
    setIsFormProcessing(true);
    const dataToSubmit = {
      policy_lifecycle_notifications: mapToApiValue(formData.policy_lifecycle_notifications),
      payments_and_reminders: mapToApiValue(formData.payments_reminders),
      account_and_security: mapToApiValue(formData.account_security),
      promotions_and_updates: mapToApiValue(formData.promotions_updates_optional),
    };
    try {
      const responseData = await updateNotificationInfo(dataToSubmit);
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.profile.update, tBe);
      }

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  useEffect(() => {
    console.log('Notification Settings Form Data:', formData);
  }, [formData]);

  return (
    <div className="mt-2 mt-md-4">
      <div className="border-bottom border-3 pb-2 border-light">
        <div className="fw-bold">{t('notifications_settings')}</div>
        <div className="text-muted mb-2">{t('we_may_still_send_you_important_notifications_about_your_account_outside_of_your_notification_settings')}</div>
      </div>
      <div className="row border-bottom border-3 pb-2 border-light mt-4 mt-md-4">
        <div className="col-12 col-md-6">
          <div className="row ">
            <div className="col-12 col-md-9 mb-3">
              <div className="fw-medium">{t('policy_lifecycle_notifications')}</div>
              <div className="text-muted">{t('covers_everything_related_to_your_insurance_policies_quotations_claims_endorsements_and_doc_availability')}</div>
            </div>
            <div className="col-12 col-md-3 mb-3">
              <div className="d-flex gap-2 mb-2">
                <ToggleButton
                  isToggled={formData.policy_lifecycle_notifications.push}
                  setIsToggled={() =>
                    setFormData((prevData) => ({
                      ...prevData,
                      policy_lifecycle_notifications: {
                        ...prevData.policy_lifecycle_notifications,
                        push: !prevData.policy_lifecycle_notifications.push,
                      },
                    }))
                  }
                />
                <div>{t('push')}</div>
              </div>
              <div className="d-flex gap-2 mb-2">
                <ToggleButton
                  isToggled={formData.policy_lifecycle_notifications.email}
                  setIsToggled={() =>
                    setFormData((prevData) => ({
                      ...prevData,
                      policy_lifecycle_notifications: {
                        ...prevData.policy_lifecycle_notifications,
                        email: !prevData.policy_lifecycle_notifications.email,
                      },
                    }))
                  }
                />
                <div>{t('email')}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="row border-bottom border-3 pb-2 border-light mt-4 mt-md-4">
        <div className="col-12 col-md-6">
          <div className="row ">
            <div className="col-12 col-md-9 mb-3">
              <div className="fw-medium">{t('payments_reminders')}</div>
              <div className="text-muted">{t('payment_due_reminders_failed_attempts_or_auto_debit_confirmations')}</div>
            </div>
            <div className="col-12 col-md-3 mb-3">
              <div className="d-flex gap-2 mb-2">
                <ToggleButton
                  isToggled={formData.payments_reminders.push}
                  setIsToggled={() =>
                    setFormData((prevData) => ({
                      ...prevData,
                      payments_reminders: {
                        ...prevData.payments_reminders,
                        push: !prevData.payments_reminders.push,
                      },
                    }))
                  }
                />
                <div>{t('push')}</div>
              </div>
              <div className="d-flex gap-2 mb-2">
                <ToggleButton
                  isToggled={formData.payments_reminders.email}
                  setIsToggled={() =>
                    setFormData((prevData) => ({
                      ...prevData,
                      payments_reminders: {
                        ...prevData.payments_reminders,
                        email: !prevData.payments_reminders.email,
                      },
                    }))
                  }
                />
                <div>{t('email')}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="row border-bottom border-3 pb-2 border-light mt-4 mt-md-4">
        <div className="col-12 col-md-6">
          <div className="row ">
            <div className="col-12 col-md-9 mb-3">
              <div className="fw-medium">{t('account_security')}</div>
              <div className="text-muted">{t('important_alerts_about_your_login_password_changes_or_system_messages')}</div>
            </div>
            <div className="col-12 col-md-3 mb-3">
              <div className="d-flex gap-2 mb-2">
                <ToggleButton
                  isToggled={formData.account_security.push}
                  setIsToggled={() =>
                    setFormData((prevData) => ({
                      ...prevData,
                      account_security: {
                        ...prevData.account_security,
                        push: !prevData.account_security.push,
                      },
                    }))
                  }
                />
                <div>{t('push')}</div>
              </div>
              <div className="d-flex gap-2 mb-2">
                <ToggleButton
                  isToggled={formData.account_security.email}
                  setIsToggled={() =>
                    setFormData((prevData) => ({
                      ...prevData,
                      account_security: {
                        ...prevData.account_security,
                        email: !prevData.account_security.email,
                      },
                    }))
                  }
                />
                <div>{t('email')}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="row border-bottom border-3 pb-2 border-light mt-4 mt-md-4">
        <div className="col-12 col-md-6">
          <div className="row ">
            <div className="col-12 col-md-9 mb-3">
              <div className="fw-medium">{t('promotions_updates_optional')}</div>
              <div className="text-muted">{t('news_offers_and_promotions_from_your_insurance_provider')}</div>
            </div>
            <div className="col-12 col-md-3 mb-3">
              <div className="d-flex gap-2 mb-2">
                <ToggleButton
                  isToggled={formData.promotions_updates_optional.push}
                  setIsToggled={() =>
                    setFormData((prevData) => ({
                      ...prevData,
                      promotions_updates_optional: {
                        ...prevData.promotions_updates_optional,
                        push: !prevData.promotions_updates_optional.push,
                      },
                    }))
                  }
                />
                <div>{t('push')}</div>
              </div>
              <div className="d-flex gap-2 mb-2">
                <ToggleButton
                  isToggled={formData.promotions_updates_optional.email}
                  setIsToggled={() =>
                    setFormData((prevData) => ({
                      ...prevData,
                      promotions_updates_optional: {
                        ...prevData.promotions_updates_optional,
                        email: !prevData.promotions_updates_optional.email,
                      },
                    }))
                  }
                />
                <div>{t('email')}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="d-flex justify-content-end gap-2 mt-3">
        <Button text={t('cancel')} color="light" width="sm" />
        <Button className="d-flex align-items-center gap-1" onClick={onSubmit} isLoading={isFormProcessing} width="sm">
          <Flexicon icon="save-01" variant="line" size={18} />
          <span>{t('save_changes')}</span>
        </Button>
      </div>
    </div>
  );
}
