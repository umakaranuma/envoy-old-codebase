'use client';

import React, { useEffect, useState } from 'react';
import { useTrans } from '@/helpers/services/lang/langService';
import { useParams, useRouter } from 'next/navigation';
import { Description } from '@/components/others/Description';
import { getOnePayments } from '../api-service';
import { formatDate, thousandSeparator } from '@/helpers/services/commonService';
import GoBack from '@/components/others/page-related/GoBack';
import { useBreadcrumb } from '@/contexts/BreadcrumbContext';

function PaymentsView() {
  const t = useTrans('label.payments,otr.common,be.msg');
  const params = useParams();
  const viewId = params.payment_id?.toString() || '';
  const router = useRouter();
  const [data, setData] = useState<any>({});
  const [skeleton, setSkeleton] = useState(false);
  const { setCustomBreadcrumb } = useBreadcrumb();

  useEffect(() => {
    setCustomBreadcrumb({
      text: data?.invoice_code,
      backurl: '/finance/a/payments',
    });
    // cleanup on unmount
    return () => setCustomBreadcrumb(null);
  }, [setCustomBreadcrumb, data]);

  // Sample payment data - replace with your actual data fetching logic
  useEffect(() => {
    const fetchData = async () => {
      const responseData = await getOnePayments(viewId);
      if (responseData?.is_success) {
        setData(responseData.result);
        setSkeleton(false);
      }
    };

    if (viewId) {
      setSkeleton(true);
      fetchData();
    }
  }, [viewId]);

  return (
    <div className="">
      <GoBack goTo={() => router.back()} title={t('payment_details')} />
      {/* Payment Information Section */}
      <div className="panel">
        <div className="panel-title">{t('payment_information')}</div>
        <div className="row">
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('debit_note_id')} value={<span className="fw-medium">{data.invoice_code || '-'}</span>} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('invoice_date')} value={<span className="fw-medium">{data.invoice_date || '-'}</span>} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('policy_info')} value={<span className="fw-medium">{data.policy_number || '-'}</span>} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('invoice_payment_type')} value={<span className="fw-medium">{data.invoice_type || '-'}</span>} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('policy_start_date')} value={data?.policy_start_date ? formatDate(data.policy_start_date) : '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('policy_end_date')} value={data?.policy_end_date ? formatDate(data.policy_end_date) : '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description
              label={t('quotation_document')}
              value={
                <a
                  href={data.document_url || '#'}
                  className="fw-medium text-decoration-none text-primary"
                  download={data.document_url ? true : undefined}
                  onClick={(e) => !data.document_url && e.preventDefault()}
                >
                  {data.quotation_document || '-'}
                </a>
              }
              skeleton={skeleton}
            />
          </div>
        </div>
      </div>

      {/* Insured Information Section */}
      <div className="panel">
        <div className="panel-title">{t('insured_information')}</div>
        <div className="row">
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('full_name')} value={<span className="fw-medium">{data.customer_name || '-'}</span>} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('primary_contact_number')} value={<span className="fw-medium">{data.customer_primary_contact || '-'}</span>} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('due_date')} value={<span className="fw-medium">{data.due_date || '-'}</span>} skeleton={skeleton} />
          </div>
        </div>
      </div>

      {/* Insurer Information Section */}
      <div className="panel">
        <div className="panel-title">{t('insurer_information')}</div>
        <div className="row">
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('account_name')} value={<span className="fw-medium">{data.insurer_info_full_name || '-'}</span>} skeleton={skeleton} />
          </div>
        </div>
      </div>

      {/* Product Information Section */}
      <div className="panel">
        <div className="panel-title">{t('product_information')}</div>
        <div className="row">
          {data.product && (
            <div className="col-12 col-md-4 mb-3">
              <Description label={t('product_name')} value={<span className="fw-medium">{data.product || '-'}</span>} skeleton={skeleton} />
            </div>
          )}
          {data.product_group && (
            <div className="col-12 col-md-4 mb-3">
              <Description label={t('product_group')} value={<span className="fw-medium">{data.product_group || '-'}</span>} skeleton={skeleton} />
            </div>
          )}
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('coverage_details')} value={<span className="fw-medium">{data.coverage_type || '-'}</span>} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('premium_amount')} value={<span className="fw-medium">{thousandSeparator(data.premium_amount) || '-'}</span>} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('amount_paid')} value={<span className="fw-medium">{thousandSeparator(data.paid_amount) || '-'}</span>} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('outstanding_amount')} value={<span className="fw-medium">{thousandSeparator(data.outstanding_amount) || '-'}</span>} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('created_by')} value={<span className="fw-medium">{data.created_by || '-'}</span>} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-4 mb-3">
            <Description label={t('updated_by')} value={<span className="fw-medium">{data.updated_by || '-'}</span>} skeleton={skeleton} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default PaymentsView;
