import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button, Input, Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { getUserLogs } from '../api-service';
import { ILoginHistory } from '../model';

function Password() {
  const t = useTrans('label.profile,otr.common');
  const [formData, setFormData] = useState<ILoginHistory[]>([]);
  const [skeleton, setSkeleton] = useState<boolean>(false);

  useEffect(() => {
    const fetchData = async () => {
      setSkeleton(true);
      const responseData = await getUserLogs();
      if (responseData?.is_success) {
        setFormData(responseData.result.data);
        setSkeleton(false);
      }
    };
    fetchData();
  }, []);
  return (
    <div className="mt-2 mt-md-4">
      <div className="border-bottom border-3 pb-2 border-light">
        <div className="fw-bold">{t('password')}</div>
        <div className="text-muted mb-2">{t('please_enter_your_current_password_to_change_your_password')}</div>
      </div>
      <div className="mt-4 mt-md-4 row">
        <div className="col-12 col-md-8">
          <div className="row">
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">{t('current_password')}</div>
            </div>
            <div className="col-12 col-md-8 mb-3">
              <Input />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">{t('new_password')}</div>
            </div>
            <div className="col-12 col-md-8 mb-3">
              <Input />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">{t('confirm_new_password')}</div>
            </div>
            <div className="col-12 col-md-8 mb-3">
              <Input />
            </div>
          </div>
        </div>
        <div className="d-flex justify-content-end gap-2 mt-3">
          <Button text={t('cancel')} color="light" width="sm" />
          <Button text={t('update_password')} width="sm" />
        </div>
      </div>
      <div className="border-bottom border-3 pb-2 border-light mt-4">
        <div className="fw-bold">{t('where_you_are_logged_in')}</div>
        {skeleton ? (
          <Skeleton width="100%" height="30px" />
        ) : (
          <div className="text-muted mb-2">
            {t('we_will_alert_you_via')} <span className="fw-semibold">{formData[0]?.email}</span> {t('if_you_are_logged_in_from_another_device')}
          </div>
        )}
      </div>
      <div>
        {skeleton ? (
          <Skeleton width="100%" height="100px" />
        ) : (
          <>
            {formData.length > 0 &&
              formData.map((log) => (
                <div className="d-flex gap-3 mt-3 border-bottom border-3 pb-2 border-light" key={log.id}>
                  <Flexicon icon="tv-01" variant="line" size={18} />
                  <div>
                    <div>{log.device}</div>
                    <div className="text-muted">
                      {log.location} • {log.login_time}
                    </div>
                  </div>
                </div>
              ))}
          </>
        )}
      </div>
    </div>
  );
}

export default Password;
