import { Description } from '@/components/others/Description';
import { formatDate, thousandSeparator } from '@/helpers/services/commonService';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button } from '@apptimus-ui/ui-element';
import { useSearchParams } from 'next/navigation';
import React, { useEffect, useState } from 'react';
import { getPolicyInfo } from '../../api-service';
import { IPolicyInfo } from '../../model';

function PolicyInfo({ setIsFormTemplateVisible, templateId, onBack }: { setIsFormTemplateVisible: Function; templateId: Function; onBack: Function }) {
  const t = useTrans('label.claim,otr.common');
  const [skeleton, setSkeleton] = useState(false);
  const [data, setData] = useState({} as IPolicyInfo);
  const searchParams = useSearchParams();
  const policyId = searchParams.get('pid') || '';

  const fetchData = async () => {
    const responseData = await getPolicyInfo(policyId);
    if (responseData?.is_success) {
      templateId(responseData.result.form_id);
      setData(responseData.result);
      setSkeleton(false);
    }
  };

  useEffect(() => {
    if (policyId) {
      setSkeleton(true);
      fetchData();
    }
  }, [policyId]);

  return (
    <>
      <div>
        <div className="bg-white custom-card overflow-hidden p-3 rounded-3 mb-3">
          <div className="fs-13 fw-semibold mb-3">{t('policyholder_info')}</div>
          <div className="row">
            {/* <div className="col-12 col-md-3 mb-3">
              <Description label={t('salutation')} value={(data?.policy_holder_info?.customer_title && data?.policy_holder_info?.customer_title) || '-'} skeleton={skeleton} />
            </div> */}
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('full_name')} value={data?.policy_holder_info?.customer_name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('primary_contact_number')} value={data?.policy_holder_info?.customer_contact_primary || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('email')} value={data?.policy_holder_info?.customer_contact_email || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('address')} value={data?.policy_holder_info?.customer_contact_address || '-'} skeleton={skeleton} />
            </div>
          </div>
        </div>
        <div className="bg-white custom-card overflow-hidden p-3 rounded-3 mb-3">
          <div className="panel-title">{t('policy_info')}</div>
          <div className="row">
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('brokerage_policy_id')} value={data?.policy_info?.brokerage_policy_id || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('insurer_policy_id')} value={data?.policy_info?.insurer_policy_id || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('start_date')} value={formatDate(data?.policy_info?.start_date) || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('end_date')} value={formatDate(data?.policy_info?.end_date) || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('risk_type')} value={data?.risk_info?.risk_type_title || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('product_name')} value={data?.product_info?.product_name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('coverage_type')} value={data?.request_info?.coverage_type_name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('sum_insured')} value={thousandSeparator(data?.policy_info?.sum_insured) || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('premium_amount')} value={thousandSeparator(data?.policy_info?.premium_amount) || '-'} skeleton={skeleton} />
            </div>
            {/* <div className="col-12 col-md-3 mb-3">
                            <Description label={t('credit_period')} value={data?.policy_info?.insurer_policy_id || '-'} skeleton={skeleton} />
                        </div>
                        <div className="col-12 col-md-3 mb-3">
                            <Description label={t('credit_age')} value={data?.policy_info?.insurer_policy_id || '-'} skeleton={skeleton} />
                        </div> */}
          </div>
        </div>
        <div className="bg-white custom-card overflow-hidden p-3 rounded-3 mb-3">
          <div className="fs-13 fw-semibold mb-3">{t('insurer_info')}</div>
          <div className="row">
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('insurer_name')} value={data?.insurer_info?.insurer_name || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('primary_contact_number')} value={data?.insurer_info?.insurer_contact_number || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('email')} value={data?.insurer_info?.insurer_mail || '-'} skeleton={skeleton} />
            </div>
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('remarks')} value={data?.insurer_info?.insurer_description || '-'} skeleton={skeleton} />
            </div>
          </div>
        </div>
      </div>
      <div className="d-flex justify-content-start gap-2 mt-3">
        <Button
          color="light"
          className="d-flex align-items-center gap-1"
          onClick={() => {
            onBack();
          }}
        >
          <Flexicon icon="chevron-left" variant="line" size={18} />
          <span className="d-none d-sm-inline">{t('back')}</span>
        </Button>
        <Button color="primary" className="d-flex align-items-center gap-1" type="submit" onClick={() => setIsFormTemplateVisible(true)}>
          <span className="d-none d-sm-inline">{t('next')}</span>
          <Flexicon icon="chevron-right" variant="line" size={18} />
        </Button>
      </div>
    </>
  );
}

export default PolicyInfo;
