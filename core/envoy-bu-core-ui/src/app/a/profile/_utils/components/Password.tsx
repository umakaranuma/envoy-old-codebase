import { useTrans } from '@/helpers/services/lang/langService';
import { Flexicon } from '@apptimus-ui/flexicon';
import { Button, Input } from '@apptimus-ui/ui-element';
import React from 'react';

function Password() {
  const t = useTrans('otr.common');
  return (
    <div className="mt-2 mt-md-4">
      <div className="border-bottom border-3 pb-2 border-light">
        <div className="fw-bold">Password</div>
        <div className="text-muted mb-2">Please enter your current password to change your password.</div>
      </div>
      <div className="mt-4 mt-md-4 row">
        <div className="col-12 col-md-8">
          <div className="row">
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">Current password</div>
            </div>
            <div className="col-12 col-md-8 mb-3">
              <Input />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">New password</div>
            </div>
            <div className="col-12 col-md-8 mb-3">
              <Input />
            </div>
            <div className="col-12 col-md-4 mb-3">
              <div className="fw-medium">Confirm new password</div>
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
        <div className="fw-bold">Where you’re logged in</div>
        <div className="text-muted mb-2">
          We’ll alert you via <span className="fw-semibold">olivia@example.com</span> if there is any unusual activity on your account.
        </div>
      </div>
      <div className="d-flex gap-3 mt-3 border-bottom border-3 pb-2 border-light">
        <Flexicon icon="tv-01" variant="line" size={18} />
        <div>
          <div>2018 Macbook Pro 15-inch</div>
          <div className="text-muted">Melbourne, Australia • 22 Jan at 10:40am</div>
        </div>
      </div>
      <div className="d-flex gap-3 mt-3 border-bottom border-3 pb-2 border-light">
        <Flexicon icon="tv-01" variant="line" size={18} />
        <div>
          <div>2018 Macbook Pro 15-inch</div>
          <div className="text-muted">Melbourne, Australia • 22 Jan at 10:40am</div>
        </div>
      </div>
    </div>
  );
}

export default Password;
