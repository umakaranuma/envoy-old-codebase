'use client';
import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import TableInView from './TableInView';
import { getOneServiceRendered } from '../api-service';
import { ServiceRenderedDetails } from '../model';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button, Label } from '@apptimus-ui/ui-element';
import CreatePayment from './CreatePayment';
import GoBack from '@/components/others/page-related/GoBack';
import { hexToRgba, thousandSeparator } from '@/helpers/services/commonService';
import { getCurrency } from '@/helpers/services/currencyService';
import { useBreadcrumb } from '@/contexts/BreadcrumbContext';

export const ServiceRenderedDetailsView = () => {
  const t = useTrans('label.service_rendered,otr.common,be.msg');
  const params = useParams();
  const router = useRouter();
  const { setCustomBreadcrumb } = useBreadcrumb();
  const currency = getCurrency();
  const viewId = params.invoiceId?.toString() || '';
  const [invoiceData, setInvoiceData] = useState<ServiceRenderedDetails | null>(null);
  const [skeleton, setSkeleton] = useState(true);
  const [tableVersion, setTableVersion] = useState(0);
  const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);
  const [paymentModalKey, setPaymentModalKey] = useState(0);

  useEffect(() => {
    setCustomBreadcrumb({
      text: invoiceData?.invoice_number,
      backurl: '/finance/a/service-rendered',
    });
    return () => setCustomBreadcrumb(null);
  }, [setCustomBreadcrumb, invoiceData]);

  const handlePaymentCreated = () => {
    setTableVersion((prev) => prev + 1);
    setPaymentModalKey((prev) => prev + 1);
    setIsPaymentModalOpen(false);
    fetchData();
  };

  useEffect(() => {
    if (viewId) {
      setSkeleton(true);
      fetchData();
    }
  }, [viewId]);

  const fetchData = async () => {
    const responseData = await getOneServiceRendered(viewId);
    if (responseData?.is_success) {
      setInvoiceData(responseData.result);
      setSkeleton(false);
    }
  };

  return (
    <div>
      <GoBack goTo={() => router.push('/finance/a/service-rendered')} title={t('service_rendered_details')} />
      {/* ServiceRendered Header Card */}
      <div className="panel">
        <div className="row">
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('debit_note_number')} value={invoiceData?.invoice_number || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('customer_name')} value={invoiceData?.customer_name || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('service_rendered')} value={invoiceData?.service_title || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('service_date')} value={invoiceData?.service_date || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('standard_fee')} value={`${currency.code} ${thousandSeparator(invoiceData?.fee as number) || '-'}`} skeleton={skeleton} />
          </div>
          {/* <div className="col-12 col-md-3 mb-3">
            <Description label={t('invoice_status')} value={invoiceData?.invoice_status_name || '-'} skeleton={skeleton} />
          </div> */}
          <div className="col-12 col-md-3 mb-3">
            <div>
              <Label label={t('payment_status')} />
            </div>
            <div
              className="rounded-5 fw-semibold badge"
              style={{ background: hexToRgba(invoiceData?.payment_status_color || '', 0.1), border: `1px solid ${invoiceData?.payment_status_color}`, color: invoiceData?.payment_status_color }}
            >
              {invoiceData?.payment_status_name}
            </div>
            {/* <Description label={t('payment_status')} value={invoiceData?.payment_status_name || '-'} skeleton={skeleton} /> */}
          </div>
          <div className="col-12 col-md-6 mb-3">
            <Description label={t('remarks')} value={invoiceData?.remarks || '-'} skeleton={skeleton} />
          </div>
          {/* <div className="col-12 col-md-3 mb-3">
            <Description label={t('created_by')} value={invoiceData?.createdBy || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('date')} value={invoiceData?.createdDate || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('updated_by')} value={invoiceData?.updatedBy || '-'} skeleton={skeleton} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('date')} value={invoiceData?.updatedDate || '-'} skeleton={skeleton} />
          </div> */}
        </div>
      </div>
      {/* ServiceRendered Payment Table */}
      <div className="bg-white custom-card overflow-hidden px-3 rounded-3 mt-3">
        <>
          <div className="d-flex align-items-center justify-content-end my-3 gap-3">
            <Button className="d-flex align-items-center gap-1" onClick={() => setIsPaymentModalOpen(true)}>
              <Flexicon icon="plus-circle" size={18} />
              <span>{t('add_settlement')}</span>
            </Button>
          </div>

          <TableInView tableVersion={tableVersion} invoiceId={viewId} />
        </>
      </div>
      {/* Payment Creation Modal */}
      {isPaymentModalOpen && (
        <CreatePayment
          key={paymentModalKey}
          isOpen={isPaymentModalOpen}
          onCancel={() => setIsPaymentModalOpen(false)}
          afterSave={handlePaymentCreated}
          invoiceData={{
            id: viewId,
            invoiceNumber: invoiceData?.invoice_number || '',
            totalAmount: Number(invoiceData?.fee || 0),
            outstandingAmount: Number(invoiceData?.outstanding_amount || 0),
          }}
        />
      )}
    </div>
  );
};
