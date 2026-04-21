import React from 'react';
import { Button, Input } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import Checkbox from '../Checkbox';

function CustomerPortal() {
  const t = useTrans('otr.common');
  return (
    <div>
      <div>
        <div className="fw-semibold">1. Policy Management Controls</div>
        <div className="ms-4 my-3">
          <Checkbox option={'Allow Auto-Renewal'} subLabel="(All policies will automatically renew)" defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
          <Checkbox option={'Enable Policy Download (PDF)'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
          <Checkbox option={'Allow Policy Cancellation Requests'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
          <Checkbox option={'Allow Policy Reinstatement Requests'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
        </div>
      </div>
      <div>
        <div className="fw-semibold">2. Self-Endorsement Rules</div>
        <div className="ms-4 my-3">
          <Checkbox option={'Enable Self-Endorsement'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
          <div className="ps-2 ps-md-3">
            <div className="fw-semibold py-2">Allowed Changes :</div>
            <div className="ps-4">
              <div className="d-flex flex-wrap gap-3">
                <Checkbox option={'Update Address'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
                <Checkbox option={'Update Contact Info'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
                <Checkbox option={'Change Beneficiary'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
                <Checkbox option={'Add/Remove Vehicle'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
              </div>
            </div>
          </div>
          <Checkbox option={'Payment Required for Changes'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
          <Checkbox option={'Reversion Time if Payment Not Made'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
        </div>
      </div>
      <div>
        <div className="fw-semibold">3. Quotation Features</div>
        <div className="ms-4 my-3">
          <Checkbox
            option={'Allow Quote Request from Portal'}
            subLabel="(You are allowed to request new quotes through the portal.)"
            defaultChecked={true}
            onChange={(option: any, checked: any) => console.log(option, checked)}
          />
          <div className="row">
            <div className="col-12 col-md-6">
              <div className="row">
                <div className="col-12 col-md-6 mb-2">
                  <Input label="Quotation Limit: " />
                </div>
                <div className="col-12 col-md-6">
                  <Input label="Quote-Enabled Product Classes: " />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div>
        <div className="fw-semibold">4. Document & Communication Settings</div>
        <div className="ms-4 my-3">
          <Checkbox option={'Allow Customers to View Uploaded Docs'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
          <Checkbox option={'Enable Notifications (Email / SMS / Push)'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
          <div className="ps-2 ps-md-3">
            <div className="fw-semibold py-2">Notification Triggers :</div>
            <div className="ps-4">
              <div className="d-flex flex-wrap gap-3">
                <Checkbox option={'Renewal'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
                <Checkbox option={'Payment Due'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
                <Checkbox option={'Quote Ready'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
              </div>
            </div>
          </div>
          <div>
            {' '}
            <Checkbox option={'Default Sender Email for Invoices'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
          </div>
        </div>
      </div>
      <div>
        <div className="fw-semibold">5. Customer Onboarding & Profile</div>
        <div className="ms-4 my-3">
          <Checkbox option={'Enable Customer Self-Onboarding'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
          <Checkbox option={'Default Sender Email for Invoices'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
        </div>
      </div>
      <div>
        <div className="fw-semibold">6. Payments & Billing</div>
        <div className="ms-4 my-3">
          <Checkbox option={'Enable Customer Self-Onboarding'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
          <Checkbox option={'Default Sender Email for Invoices'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
        </div>
      </div>
      <div>
        <div className="fw-semibold">7. Support & Interaction</div>
        <div className="ms-4 my-3">
          <Checkbox option={'Enable Customer Self-Onboarding'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
          <Checkbox option={'Default Sender Email for Invoices'} defaultChecked={true} onChange={(option: any, checked: any) => console.log(option, checked)} />
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

export default CustomerPortal;
