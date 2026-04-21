import { useTrans } from '@/helpers/services/lang/langService';
import React, { ReactNode } from 'react';

const PaymentMethodCard = ({ icon, cardNumber, expiryDate, cardName, onEdit }: { icon: ReactNode; cardNumber: string; expiryDate: string; cardName: string; onEdit: () => void }) => {
  const t = useTrans('label.profile,otr.common');
  return (
    <div className="border border-primary rounded p-2 d-flex justify-content-between mb-2 col-12 col-lg-6">
      <div className="border border-light p-2 h-50 rounded-2">{icon}</div>
      <div>
        <div>
          {cardName} ending in <span>{cardNumber}</span>
        </div>
        <div className="text-muted fs-13">
          Expiry <span>{expiryDate}</span>
        </div>
        <div className="mt-2 d-flex flex-row gap-2">
          <div className="text-muted fw-medium pointer">{t('set_as_default')}</div>
          <div className="fw-medium text-primary pointer" onClick={onEdit}>
            {t('edit')}
          </div>
        </div>
      </div>
      <div>
        <input type="checkbox" />
      </div>
    </div>
  );
};

export default PaymentMethodCard;
