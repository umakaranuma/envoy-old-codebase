'use client';

import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import PageHeading from '@/components/others/PageHeading';
import { useRouter } from 'next/navigation';
import { useState } from 'react';
import RiskRegisterList from './RiskRegisterList';
import SelectRiskData from './SelectRiskData';
function RiskRegister() {
  const router = useRouter();
  const t = useTrans('label.risk_register,otr.common');
  // const [_currentClientIds, setCurrentClientIds] = useState<string[]>([]);
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('risk_register')} icon="sun-light" />
        <div className="d-flex justify-content-end align-items-center gap-4">
          <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setIsCreateOpen(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('add_new_risk')}</span>
          </Button>
        </div>
      </div>
      <RiskRegisterList
        onEdit={(id: string) => router.push(`/policy/a/risk-register/${id}/edit`)}
        // selectedIds={(ids: string[]) => setCurrentClientIds(ids)}
        onView={(id: string) => router.push(`/policy/a/risk-register/${id}`)}
      />
      {isCreateOpen && <SelectRiskData isOpen={isCreateOpen} onCancel={() => setIsCreateOpen(false)} />}
    </>
  );
}

export default RiskRegister;
