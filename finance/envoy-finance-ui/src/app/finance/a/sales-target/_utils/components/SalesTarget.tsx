'use client';

import { Button } from '@apptimus-ui/ui-element';
import { useEffect, useState } from 'react';
import { Flexicon } from '@apptimus-ui/flexicon';
import { useTrans } from '@/helpers/services/lang/langService';
import PageHeading from '@/components/others/PageHeading';
import { useRouter, useSearchParams } from 'next/navigation';
import SalesTargetList from './SalesTargetList';
import { SalesTargetEdit } from './SalesTargetEdit';
import { toaster } from '@/helpers/services/toaster';
import { deleteSalesTarget } from '../api-service';
import { SalesTargetView } from './SalesTargetView';

function SalesTarget() {
  const t = useTrans('label.sales_target,otr.common');
  const tBe = useTrans('be.msg,be.error,be.attri');
  const router = useRouter();
  const searchParams = useSearchParams();
  const [agentTableVers, setAgentTableVers] = useState(0);
  const [teamTableVers, setTeamTableVers] = useState(0);
  const [activetab, setActiveTab] = useState('individual');
  const [currentViewId, setCurrentViewId] = useState('');
  const [currentEditId, setCurrentEditId] = useState('');

  useEffect(() => {
    const urlTab = searchParams?.get('tab') || 'individual';
    setActiveTab(urlTab);
  }, [searchParams]);

  const handleAfterUpdate = () => {
    setCurrentEditId('');
    activetab === 'individual' ? setAgentTableVers((prevTableVers) => prevTableVers + 1) : setTeamTableVers((prevTableVers) => prevTableVers + 1);
  };

  const handleOnDelete = async (deleteId: string, callback: Function, setLoader: Function, onClose: Function) => {
    setLoader(true);
    const responseData = await deleteSalesTarget(deleteId, activetab);
    setLoader(false);

    if (responseData.status_code === 409) {
      toaster.error(tBe(responseData.message));
    }

    if (responseData.is_success) {
      toaster.success(tBe(responseData.message));
      callback();
      onClose();
      activetab === 'individual' ? setAgentTableVers((prevTableVers) => prevTableVers + 1) : setTeamTableVers((prevTableVers) => prevTableVers + 1);
    }
  };

  return (
    <>
      <div className="page-header-breadcrumb custom-page-header">
        <PageHeading title={t('sales_target')} icon="sun-light" />
        <Button color="primary" className="d-flex align-items-center gap-1" onClick={() => router.push(`/finance/a/sales-target/create?tab=${activetab}`)}>
          <Flexicon icon="plus-circle" size={15} />
          <span className="d-none d-sm-inline">{t('add_new_entity', { entity: t('sales_target') })}</span>
        </Button>
      </div>
      <div className="panel mt-4">
        <div className="il-box-tab">
          <div
            className={`il-box-tab-item ${activetab === 'individual' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('individual');
              router.push(`/finance/a/sales-target?tab=individual`);
            }}
          >
            {t('individual')}
          </div>
          <div
            className={`il-box-tab-item ${activetab === 'sales-team' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('sales-team');
              router.push(`/finance/a/sales-target?tab=sales-team`);
            }}
          >
            {t('sales_team')}
          </div>
        </div>

        <SalesTargetList
          teamTableVers={teamTableVers}
          agentTableVers={agentTableVers}
          activetab={activetab}
          onEdit={(id: string) => setCurrentEditId(id)}
          handleOnDelete={handleOnDelete}
          onView={(id: string) => setCurrentViewId(id)}
        />
      </div>

      {currentEditId !== '' && <SalesTargetEdit editId={currentEditId} isOpen={currentEditId !== ''} onCancel={() => setCurrentEditId('')} afterUpdate={handleAfterUpdate} activetab={activetab} />}
      {currentViewId !== '' && (
        <SalesTargetView viewId={currentViewId} isOpen={currentViewId !== ''} onClose={() => setCurrentViewId('')} setEditId={(id: any) => setCurrentEditId(id)} activetab={activetab} />
      )}
    </>
  );
}

export default SalesTarget;
