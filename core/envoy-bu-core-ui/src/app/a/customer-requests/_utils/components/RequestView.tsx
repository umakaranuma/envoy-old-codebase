'use client';
import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button, Skeleton } from '@apptimus-ui/ui-element';
import React, { useEffect, useState } from 'react';
import { Description } from '@/components/others/Description';
import { thousandSeparator } from '@/helpers/services/commonService';
import { getOneCustomerRequest } from '../api-service';
import { ICustomerRequest } from '../model';
import { useParams, useRouter } from 'next/navigation';
import GoBack from '@/components/others/page-related/GoBack';

function RequestView() {
  const t = useTrans('label.customer_request,otr.common');
  // const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [skeleton, setSkeleton] = useState(false);
  const [data, setData] = useState<ICustomerRequest>({} as ICustomerRequest);
  const params = useParams();
  const requestId = params.requestId?.toString() || '';
  const router = useRouter();

  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOneCustomerRequest(requestId);
      if (responseData?.is_success) {
        setData(responseData.result);
        setSkeleton(false);
      }
      if (responseData.status_code === 404) {
        setSkeleton(false);
      }
    };
    if (requestId) {
      setSkeleton(true);
      fetchData();
    }
  }, [requestId]);

  async function onSubmit() {
    setIsFormProcessing(true);

    // try {
    //   const responseData = await submitPolicyInfo({ request_id: requestId, type: type });
    //   setIsFormProcessing(false);

    //   if (responseData.is_success) {
    //     toaster.success(responseData.message);
    //       router.push(`/a/customer-request`);
    //   }
    // } catch (error) {
    //   console.error('An error occurred:', error);
    // }
  }

  return (
    <>
      <div className="mb-4">
        <GoBack goTo={() => router.push(`/a/customer-requests`)} title={t('customer_request')} />
        <form onSubmit={onSubmit}>
          {skeleton ? (
            <Skeleton height="200px" width="100%" />
          ) : (
            <>
              <div className="row mt-3 panel">
                <div className="panel-title">{t('policyholder_information')}</div>
                <div className="col-12 col-md-3 mb-3">
                  <Description label={t('policyholder_name')} value={data?.policy_holder?.policy_holder_name || '-'} skeleton={skeleton} />
                </div>
                <div className="col-12 col-md-3 mb-3">
                  <Description label={t('date_of_birth')} value={data?.policy_holder?.date_of_birth || '-'} skeleton={skeleton} />
                </div>
                <div className="col-12 col-md-3 mb-3">
                  <Description label={t('gender')} value={data?.policy_holder?.gender || '-'} skeleton={skeleton} />
                </div>
                <div className="col-12 col-md-3 mb-3">
                  <Description label={t('nic_number')} value={data?.policy_holder?.nic || '-'} skeleton={skeleton} />
                </div>
                <div className="col-12 col-md-3 mb-3">
                  <Description label={t('phone_number')} value={data?.policy_holder?.phone_number || '-'} skeleton={skeleton} />
                </div>
                <div className="col-12 col-md-3 mb-3">
                  <Description label={t('email_address')} value={data?.policy_holder?.email || '-'} skeleton={skeleton} />
                </div>
                <div className="col-12 col-md-3 mb-3">
                  <Description label={t('residential_address')} value={data?.policy_holder?.address || '-'} skeleton={skeleton} />
                </div>
                <div className="col-12 col-md-3 mb-3">
                  <Description label={t('preferred_contact_method')} value={data?.policy_holder?.contact_method || '-'} skeleton={skeleton} />
                </div>
              </div>
              <div className="row mt-3 panel">
                <div className="panel-title">{t('risk_information')}</div>
                {data?.form_values?.map((item, index) => (
                  <div className="col-12 col-md-3 mb-3" key={index}>
                    <Description label={item.label ? item.label : ''} value={item.value || '-'} skeleton={skeleton} />
                  </div>
                ))}
              </div>

              <div className="row mt-3 panel">
                <div className="panel-title">{t('coverage_information')}</div>
                <div className="col-12 col-md-3 mb-3">
                  <Description label={t('sum_insured_amount')} value={thousandSeparator(data?.coverages?.sum_insured) || '-'} skeleton={skeleton} />
                </div>
                <div className="col-12 col-md-3 mb-3">
                  <Description label={t('start_date')} value={data?.coverages?.start_date || '-'} skeleton={skeleton} />
                </div>
                <div className="col-12 col-md-3 mb-3">
                  <Description label={t('end_date')} value={data?.coverages?.end_date || '-'} skeleton={skeleton} />
                </div>
              </div>
              <div className="row mt-3 panel">
                <div className="panel-title">{t('payment_information')}</div>
                <div className="col-12 col-md-3 mb-3">
                  <Description label={t('payment_method')} value={data?.payment_details?.payment_method || '-'} skeleton={skeleton} />
                </div>
                <div className="col-12 col-md-3 mb-3">
                  <Description label={t('payment_frequency')} value={data?.payment_details?.payment_frequency || '-'} skeleton={skeleton} />
                </div>
                <div className="col-12 col-md-3 mb-3">
                  <Description label={t('account_holder_name')} value={data?.payment_details?.account_holder_name || '-'} skeleton={skeleton} />
                </div>
                <div className="col-12 col-md-3 mb-3">
                  <Description label={t('bank_name')} value={data?.payment_details?.bank_name || '-'} skeleton={skeleton} />
                </div>
                <div className="col-12 col-md-3 mb-3">
                  <Description label={t('bank_branch')} value={data?.payment_details?.branch || '-'} skeleton={skeleton} />
                </div>
                <div className="col-12 col-md-3 mb-3">
                  <Description label={t('iban_swift_code_for_international_if_needed')} value={data?.payment_details?.iban_swift_code || '-'} skeleton={skeleton} />
                </div>
                <div className="col-12 col-md-3 mb-3">
                  <Description label={t('estimated_amount')} value={thousandSeparator(data?.payment_details?.estimated_amount) || '-'} skeleton={skeleton} />
                </div>
              </div>
              <div className="row mt-3 panel">
                <div className="panel-title">{t('supporting_documents_attachments')}</div>
                {data?.documents?.map((doc, index) => (
                  <div className="col-12 col-md-3 mb-3" key={index}>
                    <div className="d-flex flex-row justify-content-between gap-4 align-items-center rounded-2 p-2" style={{ borderColor: '#D0D5DD', borderWidth: '1px', borderStyle: 'solid' }}>
                      <div>{doc.value ? JSON.parse(doc.value.replace(/'/g, '"'))?.name : '-'}</div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </form>
      </div>
      <div className="d-flex justify-content-start gap-2 mt-3">
        <Button color="primary" className="d-flex align-items-center gap-1" type="submit" onClick={onSubmit} isLoading={isFormProcessing || skeleton}>
          <Flexicon icon="check-circle" variant="line" size={18} />
          <span className="d-none d-sm-inline">{t('approve')}</span>
        </Button>
      </div>
    </>
  );
}

export default RequestView;
