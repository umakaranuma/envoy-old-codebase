import React, { useEffect, useState } from 'react';
import { Button, Skeleton } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import { initApprovalPermissions } from '../commission-config/_utils/model';
import { toaster } from '@/helpers/services/toaster';
import { getApprovalPermissions, updateApprovalPermission } from '../commission-config/_utils/api-service';

function ApprovalPermissions() {
  const t = useTrans('label.general_settings,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');

  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [formData, setFormData] = useState(initApprovalPermissions);
  const [skeleton, setSkeleton] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setSkeleton(true);
        const responseData = await getApprovalPermissions();
        if (responseData?.is_success) {
          const data = JSON.parse(responseData.result.value) as any;
          onFormChange('quotation_request_approval', data.quotation_request_approval === 'true');
          onFormChange('policy_request_approval', data.policy_request_approval === 'true');
        }
      } catch (error) {
        console.log(error);
      } finally {
        setSkeleton(false);
      }
    };
    fetchData();
  }, []);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    setIsFormProcessing(true);

    try {
      const transformedData = {
        value: JSON.stringify({
          policy_request_approval: String(formData.policy_request_approval),
          quotation_request_approval: String(formData.quotation_request_approval),
        }),
      };
      const responseData = await updateApprovalPermission(transformedData);
      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
      }
    } catch (error) {
      console.error('An error occurred:', error);
    } finally {
      setIsFormProcessing(false);
    }
  }

  return (
    <div>
      <div className="mb-4">
        <div className="fw-semibold mb-3">{t('approval_permissions')}</div>
        <div className="ms-0 ms-md-3">
          {skeleton ? (
            <>
              {[1, 2].map((item) => (
                <div className="mb-3 d-flex align-items-center gap-2" key={item}>
                  <Skeleton height="20px" width="20px" className="rounded-pill" />
                  <Skeleton height="20px" width="250px" />
                </div>
              ))}
            </>
          ) : (
            <>
              <div className="form-check mb-3">
                <input
                  className="form-check-input shadow-none cursor-pointer"
                  type="checkbox"
                  name="quotation_request_approval"
                  id="quotation_request_approval"
                  checked={formData.quotation_request_approval}
                  onChange={(e) => onFormChange('quotation_request_approval', e.target.checked)}
                />
                <label className="form-check-label cursor-pointer" htmlFor="quotation_request_approval">
                  {t('quotation_request_approval')}
                </label>
              </div>
              <div className="form-check mb-3">
                <input
                  className="form-check-input shadow-none cursor-pointer"
                  type="checkbox"
                  name="policy_request_approval"
                  id="policy_request_approval"
                  checked={formData.policy_request_approval}
                  onChange={(e) => onFormChange('policy_request_approval', e.target.checked)}
                />
                <label className="form-check-label cursor-pointer" htmlFor="policy_request_approval">
                  {t('policy_request_approval')}
                </label>
              </div>
            </>
          )}
        </div>
      </div>

      <div className="d-flex justify-content-end gap-2 mt-3">
        <Button text={t('cancel')} color="light" width="sm" />
        <Button className="d-flex align-items-center gap-1" isLoading={isFormProcessing} onClick={() => onSubmit()}>
          <Flexicon icon="save-01" variant="line" size={18} />
          <span>{t('save_changes')}</span>
        </Button>
      </div>
    </div>
  );
}

export default ApprovalPermissions;
