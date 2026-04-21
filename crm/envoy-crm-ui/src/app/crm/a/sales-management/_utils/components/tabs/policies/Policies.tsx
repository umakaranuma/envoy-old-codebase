import { Flexicon } from '@apptimus-ui/flexicon';
import { Button } from '@apptimus-ui/ui-element';
import React from 'react';
import PoliciesList from './PoliciesList';
import { useTrans } from '@/helpers/services/lang/langService';
import { useRouter } from 'next/navigation';

function Policies({ leadId, customerId }: { leadId: string; customerId: string }) {
  const t = useTrans('label.sales_managements,otr.common');
  const router = useRouter();
  return (
    <div>
      {customerId && (
        <div className="d-flex justify-content-end mb-3">
          <Button
            color="primary"
            className="d-flex align-items-center gap-1"
            onClick={() => router.push(`/policy/a/policy-request/create?ip=false&cusId=${customerId}&is_renewal=false&leadId=${leadId}`)}
          >
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('add_new')}</span>
          </Button>
        </div>
      )}
      <PoliciesList />
    </div>
  );
}

export default Policies;
