import { form } from '@/constans/Form';
import { clearError, printError } from '@/helpers/handlers/validationErrorHandler';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button, Input, Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { createCoverageInfo, getOneCoverageInfo } from '../../../../api-service';
import { useSearchParams } from 'next/navigation';

function CoverageInfo({ setToggleTab, requestId, type }: { setToggleTab: Function; requestId: string | null; type: string }) {
  const t = useTrans('label.my_policy,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [formData, setFormData] = useState({ sum_insured: '', start_date: '', end_date: '' });
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [skeleton, setSkeleton] = useState(false);
  const searchParams = useSearchParams();
  const reqId = searchParams.get('reqId') || requestId;

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneCoverageInfo(reqId as string);
      if (responseData?.is_success) {
        setFormData(responseData.result);
        setSkeleton(false);
      }
      if (responseData.status_code === 404) {
        setSkeleton(false);
      }
    };
    if (reqId) {
      setSkeleton(true);
      fetchData();
    }
  }, [reqId]);

  const onFormChange = (name: string, value: any) => {
    setFormData((prevFormData) => ({ ...prevFormData, [name]: value }));
  };

  async function onSubmit() {
    clearError(form.coverage_information.store);
    setIsFormProcessing(true);

    try {
      const responseData = await createCoverageInfo({ ...formData, request_id: reqId, type: type });
      setIsFormProcessing(false);

      if (responseData.status_code === 417) {
        printError(responseData.result, form.coverage_information.store, tBe);
      }

      if (responseData.is_success) {
        setToggleTab('payment_info');
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <>
      <div className="mb-4">
        <form onSubmit={onSubmit} id={`${form.coverage_information.store}`}>
          <div className="panel-title">{t('coverage_information')}</div>
          {skeleton ? (
            <Skeleton height="200px" width="100%" />
          ) : (
            <div className="row">
              <div className="col-12 col-md-6 mb-3">
                <Input
                  isRequired
                  type="number"
                  label={t('sum_insured_amount')}
                  value={formData.sum_insured}
                  onChange={(e) => onFormChange('sum_insured', e.target.value)}
                  className="form-control error-sum_insured"
                  name="sum_insured"
                />
              </div>
              <div className="col-12 col-md-6 mb-3">
                <Input
                  isRequired
                  type="date"
                  label={t('start_date')}
                  value={formData.start_date}
                  onChange={(e) => onFormChange('start_date', e.target.value)}
                  className="form-control error-start_date"
                  name="start_date"
                />
              </div>
              <div className="col-12 col-md-6 mb-3">
                <Input
                  isRequired
                  type="date"
                  label={t('end_date')}
                  min={formData.start_date}
                  value={formData.end_date}
                  onChange={(e) => onFormChange('end_date', e.target.value)}
                  className="form-control error-end_date"
                  name="end_date"
                />
              </div>
            </div>
          )}
        </form>
      </div>
      <div className="d-flex justify-content-start gap-2 mt-3">
        <Button color="light" className="d-flex align-items-center gap-1" onClick={() => setToggleTab('personal_info')}>
          <Flexicon icon="chevron-left" variant="line" size={18} />
          <span className="d-none d-sm-inline">{t('back')}</span>
        </Button>
        <Button color="primary" className="d-flex align-items-center gap-1" type="submit" onClick={onSubmit} isLoading={isFormProcessing || skeleton}>
          <span className="d-none d-sm-inline">{t('next')}</span>
          <Flexicon icon="chevron-right" variant="line" size={18} />
        </Button>
      </div>
    </>
  );
}

export default CoverageInfo;
