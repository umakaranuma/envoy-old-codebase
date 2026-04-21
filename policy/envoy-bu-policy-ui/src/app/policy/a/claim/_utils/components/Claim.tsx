'use client';

import { Button } from '@apptimus-ui/ui-element';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import PageHeading from '@/components/others/PageHeading';
import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { sendIntimationEmail } from '../api-service';
import { toaster } from '@/helpers/services/toaster';
import SelectPolicyDetails from './claim-create/SelectPolicyDetails';
import NotifiedClaimList from './tabs/NotifiedClaimList';
import DraftClaimList from './tabs/DraftClaimList';
import EvaluatedClaimList from './tabs/EvaluatedClaimList';

function Claim() {
  const router = useRouter();
  const t = useTrans('label.claim,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const [isFormProcessing, setIsFormProcessing] = useState(false);
  const [currentClientIds, setCurrentClientIds] = useState<string[]>([]);
  const [tableVers, setTableVers] = useState(0);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [tab, setTab] = useState('draft');
  const searchParams = useSearchParams();

  const toggleTableTab = (activeTab: string) => {
    setTab(activeTab);
    router.push(`/policy/a/claim?t=${activeTab}`);
  };

  useEffect(() => {
    const tab = searchParams.get('t') || 'draft';
    toggleTableTab(tab);
  }, [searchParams]);

  async function handleSendIntimationNotice() {
    setIsFormProcessing(true);
    try {
      const responseData = await sendIntimationEmail({
        claim_ids: currentClientIds,
      });
      setIsFormProcessing(false);

      if (responseData.is_success) {
        toaster.success(tBe(responseData.message));
        setTableVers((prev) => prev + 1);
      }
    } catch (error) {
      console.error('An error occurred:', error);
    }
  }

  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('claims')} icon="sun-light" />
        <div className="d-flex justify-content-end align-items-center gap-4">
          {currentClientIds?.length > 0 && (
            <Button color="light" text={t('send_intimation')} className="d-flex align-items-center gap-1" onClick={handleSendIntimationNotice} isLoading={isFormProcessing} />
          )}
          <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => setIsCreateOpen(true)}>
            <Flexicon icon="plus-circle" size={18} />
            <span className="d-none d-sm-inline">{t('raise_new_claim')}</span>
          </Button>
        </div>
      </div>
      <div className="panel mt-2">
        <div className="il-box-tab mb-3">
          <div className={`il-box-tab-item ${tab === 'draft' ? 'active' : ''}`} onClick={() => toggleTableTab('draft')}>
            {t('draft')}
          </div>
          <div className={`il-box-tab-item ${tab === 'notified' ? 'active' : ''}`} onClick={() => toggleTableTab('notified')}>
            {t('notified')}
          </div>
          <div className={`il-box-tab-item ${tab === 'evaluated' ? 'active' : ''}`} onClick={() => toggleTableTab('evaluated')}>
            {t('evaluated')}
          </div>
        </div>
        {tab === 'notified' && (
          <NotifiedClaimList
            onEdit={(id: string) => router.push(`/policy/a/claim/${id}/edit`)}
            tableVers={tableVers}
            onView={(id: string, policyId: string, templateId: string) => router.push(`/policy/a/claim/${id}?pid=${policyId}&tid=${templateId}`)}
            selectedIds={setCurrentClientIds}
          />
        )}
        {tab === 'draft' && (
          <DraftClaimList
            onEdit={(id: string) => router.push(`/policy/a/claim/${id}/edit`)}
            tableVers={tableVers}
            onView={(id: string, policyId: string, templateId: string) => router.push(`/policy/a/claim/${id}?pid=${policyId}&tid=${templateId}`)}
            selectedIds={setCurrentClientIds}
          />
        )}
        {tab === 'evaluated' && (
          <EvaluatedClaimList
            onEdit={(id: string) => router.push(`/policy/a/claim/${id}/edit`)}
            tableVers={tableVers}
            onView={(id: string, policyId: string, templateId: string) => router.push(`/policy/a/claim/${id}?pid=${policyId}&tid=${templateId}`)}
            selectedIds={setCurrentClientIds}
          />
        )}
      </div>
      {isCreateOpen && <SelectPolicyDetails isOpen={isCreateOpen} onCancel={() => setIsCreateOpen(false)} />}
    </>
  );
}

export default Claim;
