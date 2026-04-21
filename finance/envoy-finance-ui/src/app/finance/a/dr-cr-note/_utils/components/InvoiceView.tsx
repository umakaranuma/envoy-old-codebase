'use client';
import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Description } from '@/components/others/Description';
import { useTrans } from '@/helpers/services/lang/langService';
import PaymentList from './view/PaymentList';
import { Button, Label } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { InvoiceDetails } from '../model';
import CreatePayment from './view/CreatePayment';
import { getOneInvoice } from '../api-service';
import { formatDate, hexToRgba, thousandSeparator } from '@/helpers/services/commonService';
import { getCurrency } from '@/helpers/services/currencyService';
import GoBack from '@/components/others/page-related/GoBack';
import { useBreadcrumb } from '@/contexts/BreadcrumbContext';
import InvoiceType from './InvoiceType';

export const InvoiceDetailsView = () => {
  const t = useTrans('label.invoice,otr.common,be.msg');
  const params = useParams();
  const router = useRouter();
  const { setCustomBreadcrumb } = useBreadcrumb();
  const invoiceId = params.drCrNoteId?.toString() || '';
  const currency = getCurrency();
  const [invoiceData, setInvoiceData] = useState<InvoiceDetails | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);
  const [tableVersion, setTableVersion] = useState(0);
  const [paymentModalKey, setPaymentModalKey] = useState(0);

  useEffect(() => {
    setCustomBreadcrumb({
      text: invoiceData?.invoice_number,
      backurl: '/finance/a/dr-cr-note',
    });
    return () => setCustomBreadcrumb(null);
  }, [setCustomBreadcrumb, invoiceData]);

  // Fetch invoice data
  useEffect(() => {
    const fetchInvoiceData = async () => {
      try {
        setIsLoading(true);
        const response = await getOneInvoice(invoiceId);
        if (response?.is_success) {
          setInvoiceData(response.result);
        }
      } catch (error) {
        console.error('Error fetching invoice:', error);
      } finally {
        setIsLoading(false);
      }
    };

    if (invoiceId) {
      fetchInvoiceData();
    }
  }, [invoiceId, tableVersion]);

  const handlePaymentCreated = () => {
    setTableVersion((prev) => prev + 1);
    setPaymentModalKey((prev) => prev + 1);
    setIsPaymentModalOpen(false);
  };

  return (
    <div className="invoice-details-container">
      <GoBack goTo={() => router.push('/finance/a/dr-cr-note')} title={t('dr_cr_note_details')} />
      <div className="panel">
        <div className="row">
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('dr_cr_note_number')} value={invoiceData?.invoice_number || '-'} skeleton={isLoading} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('dr_cr_note_date')} value={invoiceData?.invoice_date || '-'} skeleton={isLoading} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description
              label={t('policy_info')}
              value={invoiceData?.policy_number || '-'}
              skeleton={isLoading}
              isClickable
              onclick={() => {
                router.push(`/policy/a/issued-policies/${invoiceData?.issued_policy_id}`);
              }}
            />
          </div>
          {invoiceData?.product && (
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('product_name')} value={invoiceData?.product || '-'} skeleton={isLoading} />
            </div>
          )}
          {invoiceData?.product_group && (
            <div className="col-12 col-md-3 mb-3">
              <Description label={t('product_group')} value={invoiceData?.product_group || '-'} skeleton={isLoading} />
            </div>
          )}
          <div className="col-12 col-md-3 mb-3">
            <div>
              <Label label={t('type')} />
            </div>
            <InvoiceType type={invoiceData?.invoice_type as string} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('policy_start_date')} value={invoiceData?.policy_start_date ? formatDate(invoiceData.policy_start_date) : '-'} skeleton={isLoading} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('policy_end_date')} value={invoiceData?.policy_end_date ? formatDate(invoiceData.policy_end_date) : '-'} skeleton={isLoading} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('transaction_type')} value={invoiceData?.transaction_type_name || '-'} skeleton={isLoading} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('dr_cr_note_amount')} value={`${currency.code} ${thousandSeparator(invoiceData?.invoice_amount as string) || '-'}`} skeleton={isLoading} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('paid_amt')} value={`${currency.code} ${thousandSeparator(invoiceData?.paid_amount as string) || '-'}`} skeleton={isLoading} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('out_amt')} value={`${currency.code} ${thousandSeparator(invoiceData?.outstanding_amount as string) || '-'}`} skeleton={isLoading} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('due_dte')} value={invoiceData?.due_date || '-'} skeleton={isLoading} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('last_paid_date')} value={invoiceData?.last_paid_date || '-'} skeleton={isLoading} />
          </div>

          <div className="col-12 col-md-3 mb-3">
            <Description label={t('credit_age_days')} value={invoiceData?.credit_age_days || '0'} skeleton={isLoading} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('credit_period_days')} value={invoiceData?.credit_period_days || '0'} skeleton={isLoading} />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description
              label={t('status')}
              value={
                // invoiceData?.invoice_status_name || '-'
                <div
                  className="rounded-5 fw-semibold badge"
                  style={{ background: hexToRgba(invoiceData?.invoice_status_color || '', 0.1), border: `1px solid ${invoiceData?.invoice_status_color}`, color: invoiceData?.invoice_status_color }}
                >
                  {invoiceData?.invoice_status_name}
                </div>
              }
              skeleton={isLoading}
            />
          </div>
          <div className="col-12 col-md-3 mb-3">
            <Description label={t('remarks')} value={invoiceData?.remarks || '-'} skeleton={isLoading} />
          </div>
        </div>
      </div>

      <div className="bg-white custom-card overflow-hidden px-3 rounded-3 mt-3">
        <div className="d-flex align-items-center justify-content-between my-3 gap-3">
          <div className="panel-title"> {t('payments')}</div>
          <Button className="d-flex align-items-center gap-1" onClick={() => setIsPaymentModalOpen(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span>{t('add_settlement')}</span>
          </Button>
        </div>
        <PaymentList tableVersion={tableVersion} invoiceId={invoiceId} />
      </div>

      {/* Payment Creation Modal */}
      {isPaymentModalOpen && invoiceData && (
        <CreatePayment
          key={paymentModalKey}
          isOpen={isPaymentModalOpen}
          onCancel={() => setIsPaymentModalOpen(false)}
          afterSave={handlePaymentCreated}
          invoiceData={{
            id: invoiceId,
            invoiceNumber: invoiceData.invoice_number,
            totalAmount: Number(invoiceData.invoice_amount),
            outstandingAmount: Number(invoiceData.outstanding_amount),
          }}
        />
      )}
    </div>
  );
};
