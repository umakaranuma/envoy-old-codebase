import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button, Input } from '@apptimus-ui/ui-element';
import React from 'react';

function PaymentMethod() {
  const t = useTrans('otr.common');
  return (
    <div className="mt-2 mt-md-4">
      <div className="border-bottom border-3 pb-2 border-light">
        <div className="fw-bold">Payment method</div>
        <div className="text-muted mb-2">Update your payment method details and payment gateway.</div>
      </div>
      <div className="row border-bottom border-3 pb-2 border-light mt-4 mt-md-4">
        <div className="col-12 col-md-8">
          <div className="row ">
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">Contact email</div>
              <div className="text-muted">Where should Payment Receipt be sent?</div>
            </div>
            <div className="col-12 col-md-8 mb-3">
              <Input label="Send to my account email" />
              <Input label="Send to an alternative email" />
            </div>
          </div>
        </div>
      </div>
      <div className="row border-bottom border-3 pb-2 border-light mt-4 mt-md-4">
        <div className="col-12 col-md-4 mb-3">
          <div className="fw-medium">Bank Transfer</div>
          <div className="text-muted">Enter your bank account details. These details will be shown to customers opting for a bank transfer</div>
        </div>
        <div className="col-12 col-md-8 mb-3">
          <div className="fw-bold">Bank Account Info</div>
          <div className="row">
            <div className="col-12 col-md-6 mb-3">
              <Input label="Account Holder Name" />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input label="Bank Name" />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input label="Bank Branch" />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input label="Account Number" />
            </div>
            <div className="col-12 col-md-6 mb-3">
              <Input label="IBAN/Swift Code (for international if needed)" />
            </div>
          </div>
        </div>
      </div>

      <div className="d-flex justify-content-end gap-2 mt-3">
        <Button text={t('cancel')} color="light" width="sm" />
        <Button className="d-flex align-items-center gap-1">
          <Flexicon icon="save-01" variant="line" size={18} />
          <span>{t('save_changes')}</span>
        </Button>
      </div>
    </div>
  );
}

export default PaymentMethod;
